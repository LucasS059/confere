import { z } from "zod";

export namespace ProjectModel {
  export const createInput = z.object({
    name: z.string().min(1, "Nome do projeto é obrigatório"),
    rawRubric: z.string().min(1, "A rubrica ou edital é obrigatório"),
    description: z.string().optional(),
    sourceType: z.enum(["Texto", "PDF/DOCX"]).default("Texto"),
    rubricFilename: z.string().optional(),
    initialRequirements: z.array(z.string()).optional(),
    // Entrega inicial opcional vinculada à criação
    initialSubmission: z
      .object({
        filename: z.string().min(1),
        fileSize: z.string().optional(),
        totalPages: z.number().optional(),
        version: z.string().default("v1"),
      })
      .optional(),
  });

  export const addRequirementInput = z.object({
    projectId: z.string().min(1),
    title: z.string().min(1),
    description: z.string().optional(),
  });

  export const toggleRequirementInput = z.object({
    requirementId: z.string().min(1),
    checked: z.boolean(),
  });

  export const addSubmissionInput = z.object({
    projectId: z.string().min(1),
    filename: z.string().min(1),
    version: z.string().default("v1"),
    fileSize: z.string().optional(),
    totalPages: z.number().optional(),
  });
}

