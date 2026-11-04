import { and, db, desc, eq } from "@confere/db";
import { project, requirement, submission } from "@confere/db/schema/project";
import { TRPCError } from "@trpc/server";
import type { ProjectModel } from "./model";

function generateId(): string {
  return Math.random().toString(36).substring(2, 10) + Date.now().toString(36);
}

export abstract class ProjectService {
  static async listUserProjects(userId: string) {
    const projects = await db.query.project.findMany({
      where: eq(project.userId, userId),
      orderBy: [desc(project.createdAt)],
      with: {
        requirements: true,
        submissions: {
          orderBy: [desc(submission.createdAt)],
          limit: 1,
        },
      },
    });

    return projects.map((p) => {
      const latest = p.submissions[0];
      return {
        id: p.id,
        name: p.name,
        rawRubric: p.rawRubric,
        sourceType: p.sourceType,
        createdAt: p.createdAt,
        requirementsCount: p.requirements.length,
        latestSubmission: latest
          ? {
              id: latest.id,
              version: latest.version,
              filename: latest.filename,
              coverage: latest.coverage,
              status: latest.status,
              createdAt: latest.createdAt,
            }
          : null,
      };
    });
  }

  static async getProjectById(userId: string, projectId: string) {
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
  }

  static async createProject(
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

    // Requisitos iniciais (se informados ou extraídos)
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

    // Se o aluno anexou o trabalho inicial logo no cadastro
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
          status: "concluido",
          coverage: 100,
        })
        .returning();
      initialSub = createdSub;
    }

    return {
      ...newProject,
      submission: initialSub,
    };
  }

  static async addRequirement(
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
  }

  static async toggleRequirement(
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
  }

  static async addSubmission(
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

    const [sub] = await db
      .insert(submission)
      .values({
        id: generateId(),
        projectId: input.projectId,
        filename: input.filename,
        version: input.version,
        fileSize: input.fileSize,
        totalPages: input.totalPages,
        status: "concluido",
        coverage: 100,
      })
      .returning();

    return sub;
  }
}
