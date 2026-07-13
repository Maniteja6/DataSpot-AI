# DataSpot AI — Deployment Notes

This document covers deploying the frontend to **Vercel** and the backend
(FastAPI + AWS Bedrock AgentCore + RAG) to **AWS**, plus the AWS resources
defined under `infra/aws/`.

---

## 1. Architecture summary

```
┌──────────────┐        HTTPS         ┌───────────────────┐
│  Vercel       │ ───────────────────▶ │  FastAPI backend   │
│  (Next.js)    │ ◀─────────────────── │  (ECS Fargate / EC2)│
└──────────────┘                      └─────────┬──────────┘
                                                  │
                     ┌────────────────────────────┼────────────────────────────┐
                     ▼                            ▼                            ▼
            ┌─────────────────┐         ┌──────────────────┐        ┌──────────────────┐
            │ Bedrock AgentCore│         │   Amazon S3        │        │ OpenSearch        │
            │ (8 agents +      │         │ (dataset storage)  │        │ Serverless         │
            │  orchestrator)   │         └──────────────────┘        │ (RAG vector store) │
            └─────────────────┘                                      └──────────────────┘
                     │
                     ▼
            ┌─────────────────┐
            │ CloudWatch Logs  │
            │ (per-agent +     │
            │  API log groups) │
            └─────────────────┘
```

## 2. Prerequisites

- AWS account with Bedrock model access enabled for:
  - `anthropic.claude-3-5-sonnet-20241022-v2:0`
  - `anthropic.claude-3-5-haiku-20241022-v1:0`
  - `amazon.titan-embed-text-v2:0`
- AWS CLI configured (`aws configure`) with permissions to create IAM roles,
  S3 buckets, OpenSearch Serverless collections, and CloudFormation stacks.
- Vercel account + the `vercel` CLI, or the Vercel Git integration.
- Node.js 20+, Python 3.11+.

## 3. Deploy AWS infrastructure

Run these from `infra/aws/`, in order:

```bash
# 1. Create the S3 bucket for dataset storage (if it doesn't already exist)
aws s3 mb s3://dataspot-ai-datasets --region us-east-1
aws s3api put-bucket-encryption \
  --bucket dataspot-ai-datasets \
  --server-side-encryption-configuration '{"Rules":[{"ApplyServerSideEncryptionByDefault":{"SSEAlgorithm":"AES256"}}]}'

# 2. Apply the bucket policy (replace <ACCOUNT_ID> placeholders first)
aws s3api put-bucket-policy \
  --bucket dataspot-ai-datasets \
  --policy file://s3_bucket_policy.json

# 3. Create the backend + AgentCore IAM roles, attaching iam_policy.json
#    as an inline/managed policy on each role's trust relationship
#    (ecs-tasks.amazonaws.com for the backend, bedrock-agentcore.amazonaws.com
#    for the AgentCore runtime role).

# 4. Deploy CloudWatch log groups
aws cloudformation deploy \
  --template-file cloudwatch_log_groups.yaml \
  --stack-name dataspot-ai-logs

# 5. Deploy the OpenSearch Serverless vector store
aws cloudformation deploy \
  --template-file opensearch_serverless_config.yaml \
  --stack-name dataspot-ai-vectors \
  --parameter-overrides \
      BackendRoleArn=arn:aws:iam::<ACCOUNT_ID>:role/dataspot-ai-backend-role \
      AgentCoreRoleArn=arn:aws:iam::<ACCOUNT_ID>:role/dataspot-ai-agentcore-runtime-role

# 6. Register the Bedrock AgentCore runtime + 8 agents using
#    bedrock_agentcore_config.yaml as the source of truth (via the AgentCore
#    console, CLI, or the backend's agent_registry.py bootstrap script).
```

After step 5, copy the `CollectionEndpoint` output into
`backend/.env` as `OPENSEARCH_COLLECTION_ENDPOINT`, then create the vector
index using the schema documented at the bottom of
`opensearch_serverless_config.yaml`.

## 4. Deploy the backend (FastAPI)

The backend is container-friendly. A minimal path using ECS Fargate:

```bash
cd backend
docker build -t dataspot-ai-backend .
aws ecr create-repository --repository-name dataspot-ai-backend
docker tag dataspot-ai-backend:latest <ACCOUNT_ID>.dkr.ecr.us-east-1.amazonaws.com/dataspot-ai-backend:latest
docker push <ACCOUNT_ID>.dkr.ecr.us-east-1.amazonaws.com/dataspot-ai-backend:latest
# then create/update an ECS service pointing at that image, with the
# dataspot-ai-backend-role attached and env vars from backend/.env.example
```

For local development instead:

```bash
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

## 5. Deploy the frontend (Vercel)

```bash
cd frontend
vercel link
vercel env add NEXT_PUBLIC_API_BASE_URL   # your deployed backend URL
vercel env add NEXT_PUBLIC_USE_MOCKS      # set to "false" once the backend is live
vercel deploy --prod
```

Or connect the repo in the Vercel dashboard and set the same two environment
variables under Project Settings → Environment Variables — Vercel will pick
up `vercel.json` automatically.

## 6. Post-deploy checklist

- [ ] Confirm `GET {API_BASE_URL}/health` (or equivalent) responds from the
      deployed backend before flipping `NEXT_PUBLIC_USE_MOCKS` to `false`.
- [ ] Confirm CORS on the backend allows the Vercel deployment origin
      (`ALLOWED_ORIGINS` in `backend/.env`).
- [ ] Upload a small test dataset end-to-end and confirm the pipeline stages
      in the Dashboard's Agent Activity Timeline move from `queued` →
      `running` → `complete`.
- [ ] Ask the Chat Assistant a question about that dataset and confirm the
      response includes at least one citation card.
- [ ] Check CloudWatch under `/dataspot-ai/*` log groups for agent traces.

## 7. Notes on scope

This is a working prototype, not a hardened production platform:
authentication, multi-tenant isolation, rate limiting, and fine-grained
IAM scoping (the `iam_policy.json` here is intentionally broad for ease of
local iteration) should all be tightened before handling real customer data.
