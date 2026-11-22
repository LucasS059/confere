import { and, db, desc, eq } from "@confere/db";
import { project, requirement, submission } from "@confere/db/schema/project";
import { TRPCError } from "@trpc/server";
import type { ProjectModel } from "./model";

function generateId(): string {
  return crypto.randomUUID();
}

function buildSubmissionKey(projectId: string, filename: string): string {
  const safeName = filename.replace(/[^a-zA-Z0-9._-]/g, "_");
  return `submissions/${projectId}/${Date.now()}-${safeName}`;
}

// Em dev sem S3 configurado, retorna null para permitir fallback local em getUploadUrl.
async function getOptionalS3Bucket() {
  const s3Bucket = process.env.S3_BUCKET?.trim();
  if (!s3Bucket) {
    if (process.env.NODE_ENV === "production") {
      throw new TRPCError({
        code: "INTERNAL_SERVER_ERROR",
        message: "Armazenamento S3 não configurado no servidor",
      });
    }
    return null;
  }

  const { createS3BucketFromEnv } = await import("@confere/storage");
  return createS3BucketFromEnv({
    S3_BUCKET: s3Bucket,
    S3_REGION: process.env.S3_REGION,
    S3_ENDPOINT: process.env.S3_ENDPOINT,
    S3_ACCESS_KEY_ID: process.env.S3_ACCESS_KEY_ID,
    S3_SECRET_ACCESS_KEY: process.env.S3_SECRET_ACCESS_KEY,
  });
}

export const ProjectService = {
  async listUserProjects(userId: string) {
    const projects = await db.query.project.findMany({
      where: eq(project.userId, userId),
      orderBy: [desc(project.createdAt)],
      with: {
        requirements: true,
        submissions: {
          orderBy: [desc(submission.createdAt)],
          with: {
            results: true,
          },
        },
      },
    });

    return projects.map((p) => {
      // A relação submissions já vem ordenada da mais recente para a mais antiga.
      const latest = p.submissions[0];
      const latestResults = latest?.results ?? [];
      const atendidosCount = latestResults.filter(
        (r) => r.status === "atendido",
      ).length;
      const revisarCount = latestResults.filter(
        (r) => r.status === "revisar",
      ).length;
      const faltandoCount = latestResults.filter(
        (r) => r.status === "faltando",
      ).length;

      return {
        id: p.id,
        name: p.name,
        description: p.description,
        rawRubric: p.rawRubric,
        sourceType: p.sourceType,
        createdAt: p.createdAt,
        requirementsCount: p.requirements.length,
        submissionsCount: p.submissions.length,
        latestSubmission: latest
          ? {
              id: latest.id,
              version: latest.version,
              filename: latest.filename,
              fileSize: latest.fileSize,
              totalPages: latest.totalPages,
              coverage: latest.coverage,
              status: latest.status,
              createdAt: latest.createdAt,
              atendidosCount,
              revisarCount,
              faltandoCount,
            }
          : null,
      };
    });
  },

  async getProjectById(userId: string, projectId: string) {
    const item = await db.query.project.findFirst({
      where: and(eq(project.id, projectId), eq(project.userId, userId)),
      with: {
        requirements: {
          orderBy: [requirement.order, requirement.createdAt],
        },
        submissions: {
          orderBy: [desc(submission.createdAt)],
          with: {
            results: true,
          },
        },
      },
    });

    if (!item) {
      throw new TRPCError({
        code: "NOT_FOUND",
        message: "Projeto não encontrado",
      });
    }

    return item;
  },

  async createProject(
    userId: string,
    input: typeof ProjectModel.createInput._output,
  ) {
    const projectId = generateId();

    const [newProject] = await db
      .insert(project)
      .values({
        id: projectId,
        userId,
        name: input.name,
        description: input.description,
        rawRubric: input.rawRubric,
        sourceType: input.sourceType,
        rubricFilename: input.rubricFilename,
      })
      .returning();

    const reqs =
      input.initialRequirements?.filter((r) => r.trim().length > 0) || [];
    if (reqs.length > 0) {
      await db.insert(requirement).values(
        reqs.map((title, index) => ({
          id: generateId(),
          projectId,
          title: title.trim(),
          order: index,
          checked: true,
        })),
      );
    }

    let initialSub = null;
    if (input.initialSubmission) {
      const [createdSub] = await db
        .insert(submission)
        .values({
          id: generateId(),
          projectId,
          filename: input.initialSubmission.filename,
          version: input.initialSubmission.version || "v1",
          fileSize: input.initialSubmission.fileSize,
          totalPages: input.initialSubmission.totalPages,
          status: "aguardando_analise",
          coverage: null,
        })
        .returning();
      initialSub = createdSub;
    }

    return {
      ...newProject,
      submission: initialSub,
    };
  },

  async updateRubric(
    userId: string,
    input: typeof ProjectModel.updateRubricInput._output,
  ) {
    const [updated] = await db
      .update(project)
      .set({ rawRubric: input.rawRubric.trim() })
      .where(and(eq(project.id, input.projectId), eq(project.userId, userId)))
      .returning();

    if (!updated) {
      throw new TRPCError({
        code: "NOT_FOUND",
        message: "Projeto não encontrado",
      });
    }

    return updated;
  },

  async addRequirement(
    userId: string,
    input: typeof ProjectModel.addRequirementInput._output,
  ) {
    const proj = await db.query.project.findFirst({
      where: and(eq(project.id, input.projectId), eq(project.userId, userId)),
    });

    if (!proj) {
      throw new TRPCError({
        code: "FORBIDDEN",
        message: "Projeto não pertence ao usuário",
      });
    }

    const [item] = await db
      .insert(requirement)
      .values({
        id: generateId(),
        projectId: input.projectId,
        title: input.title,
        description: input.description,
        checked: true,
      })
      .returning();

    return item;
  },

  async toggleRequirement(
    userId: string,
    input: typeof ProjectModel.toggleRequirementInput._output,
  ) {
    const req = await db.query.requirement.findFirst({
      where: eq(requirement.id, input.requirementId),
      with: { project: true },
    });

    if (!req || req.project.userId !== userId) {
      throw new TRPCError({
        code: "FORBIDDEN",
        message: "Requisito não encontrado ou sem permissão",
      });
    }

    const [updated] = await db
      .update(requirement)
      .set({ checked: input.checked })
      .where(eq(requirement.id, input.requirementId))
      .returning();

    return updated;
  },

  async deleteRequirement(
    userId: string,
    input: typeof ProjectModel.deleteRequirementInput._output,
  ) {
    const req = await db.query.requirement.findFirst({
      where: eq(requirement.id, input.requirementId),
      with: { project: true },
    });

    if (!req || req.project.userId !== userId) {
      throw new TRPCError({
        code: "FORBIDDEN",
        message: "Requisito não encontrado ou sem permissão",
      });
    }

    const [deleted] = await db
      .delete(requirement)
      .where(eq(requirement.id, input.requirementId))
      .returning();

    return deleted;
  },

  async getUploadUrl(
    userId: string,
    input: typeof ProjectModel.getUploadUrlInput._output,
  ) {
    const proj = await db.query.project.findFirst({
      where: and(eq(project.id, input.projectId), eq(project.userId, userId)),
    });

    if (!proj) {
      throw new TRPCError({
        code: "FORBIDDEN",
        message: "Projeto não pertence ao usuário",
      });
    }

    const key = buildSubmissionKey(input.projectId, input.filename);
    const s3 = await getOptionalS3Bucket();

    if (s3) {
      const uploadUrl = await s3.getUploadSignedUrl(
        key,
        input.contentType || "application/octet-stream",
      );
      return {
        mode: "s3" as const,
        uploadUrl,
        key,
      };
    }

    return {
      mode: "local" as const,
      uploadUrl: null,
      key: `local://${key}`,
    };
  },

  async addSubmission(
    userId: string,
    input: typeof ProjectModel.addSubmissionInput._output,
  ) {
    const proj = await db.query.project.findFirst({
      where: and(eq(project.id, input.projectId), eq(project.userId, userId)),
    });

    if (!proj) {
      throw new TRPCError({
        code: "FORBIDDEN",
        message: "Projeto não pertence ao usuário",
      });
    }

    const resolvedFileUrl =
      input.fileUrl ??
      `local://${buildSubmissionKey(input.projectId, input.filename)}`;

    // A chave vem do cliente: só aceita arquivos sob o prefixo deste projeto.
    const keyPrefix = `submissions/${input.projectId}/`;
    if (
      !resolvedFileUrl.startsWith(keyPrefix) &&
      !resolvedFileUrl.startsWith(`local://${keyPrefix}`)
    ) {
      throw new TRPCError({
        code: "BAD_REQUEST",
        message: "Arquivo da entrega inválido para este projeto",
      });
    }

    const versionDisplay = input.label?.trim()
      ? `${input.version.trim()} · ${input.label.trim()}`
      : input.version.trim();

    const [sub] = await db
      .insert(submission)
      .values({
        id: generateId(),
        projectId: input.projectId,
        filename: input.filename,
        version: versionDisplay,
        fileUrl: resolvedFileUrl,
        fileSize: input.fileSize,
        totalPages: input.totalPages,
        status: "aguardando_analise",
        coverage: null,
      })
      .returning();

    return sub;
  },
};
