import { z } from "zod";
import { protectedProcedure, router } from "../../index";
import { ProjectModel } from "./model";
import { ProjectService } from "./service";

export const projectRouter = router({
  list: protectedProcedure.query(({ ctx }) =>
    ProjectService.listUserProjects(ctx.session.user.id),
  ),

  getById: protectedProcedure
    .input(z.object({ id: z.string().min(1) }))
    .query(({ ctx, input }) =>
      ProjectService.getProjectById(ctx.session.user.id, input.id),
    ),

  create: protectedProcedure
    .input(ProjectModel.createInput)
    .mutation(({ ctx, input }) =>
      ProjectService.createProject(ctx.session.user.id, input),
    ),

  updateRubric: protectedProcedure
    .input(ProjectModel.updateRubricInput)
    .mutation(({ ctx, input }) =>
      ProjectService.updateRubric(ctx.session.user.id, input),
    ),

  addRequirement: protectedProcedure
    .input(ProjectModel.addRequirementInput)
    .mutation(({ ctx, input }) =>
      ProjectService.addRequirement(ctx.session.user.id, input),
    ),

  toggleRequirement: protectedProcedure
    .input(ProjectModel.toggleRequirementInput)
    .mutation(({ ctx, input }) =>
      ProjectService.toggleRequirement(ctx.session.user.id, input),
    ),

  deleteRequirement: protectedProcedure
    .input(ProjectModel.deleteRequirementInput)
    .mutation(({ ctx, input }) =>
      ProjectService.deleteRequirement(ctx.session.user.id, input),
    ),

  getUploadUrl: protectedProcedure
    .input(ProjectModel.getUploadUrlInput)
    .mutation(({ ctx, input }) =>
      ProjectService.getUploadUrl(ctx.session.user.id, input),
    ),

  addSubmission: protectedProcedure
    .input(ProjectModel.addSubmissionInput)
    .mutation(({ ctx, input }) =>
      ProjectService.addSubmission(ctx.session.user.id, input),
    ),
});
