import "dotenv/config";
import { z } from "zod";

const envSchema = z.object({
  DATABASE_URL: z.string().min(1),
  BETTER_AUTH_SECRET: z.string().min(32),
  BETTER_AUTH_URL: z.url().default("http://localhost:3000"),
  CORS_ORIGIN: z.url().default("http://localhost:8081"),
  NODE_ENV: z
    .enum(["development", "production", "test"])
    .default("development"),
  S3_BUCKET: z.string().optional(),
  S3_REGION: z.string().optional(),
  S3_ENDPOINT: z.string().optional(),
  S3_ACCESS_KEY_ID: z.string().optional(),
  S3_SECRET_ACCESS_KEY: z.string().optional(),
});

export const env = process.env.SKIP_ENV_VALIDATION
  ? (process.env as unknown as z.infer<typeof envSchema>)
  : envSchema.parse(process.env);
