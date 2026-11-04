import { relations } from "drizzle-orm";
import { boolean, index, integer, pgTable, text, timestamp } from "drizzle-orm/pg-core";
import { user } from "./auth";

export const project = pgTable(
  "project",
  {
    id: text("id").primaryKey(),
    userId: text("user_id")
      .notNull()
      .references(() => user.id, { onDelete: "cascade" }),
    name: text("name").notNull(),
    description: text("description"),
    rawRubric: text("raw_rubric").notNull(),
    sourceType: text("source_type").default("Texto").notNull(),
    rubricFilename: text("rubric_filename"),
    createdAt: timestamp("created_at").defaultNow().notNull(),
    updatedAt: timestamp("updated_at")
      .defaultNow()
      .$onUpdate(() => /* @__PURE__ */ new Date())
      .notNull(),
  },
  (table) => [index("project_userId_idx").on(table.userId)],
);

export const requirement = pgTable(
  "requirement",
  {
    id: text("id").primaryKey(),
    projectId: text("project_id")
      .notNull()
      .references(() => project.id, { onDelete: "cascade" }),
    title: text("title").notNull(),
    description: text("description"),
    checked: boolean("checked").default(true).notNull(),
    order: integer("order").default(0).notNull(),
    createdAt: timestamp("created_at").defaultNow().notNull(),
    updatedAt: timestamp("updated_at")
      .defaultNow()
      .$onUpdate(() => /* @__PURE__ */ new Date())
      .notNull(),
  },
  (table) => [index("requirement_projectId_idx").on(table.projectId)],
);

export const submission = pgTable(
  "submission",
  {
    id: text("id").primaryKey(),
    projectId: text("project_id")
      .notNull()
      .references(() => project.id, { onDelete: "cascade" }),
    version: text("version").default("v1").notNull(),
    filename: text("filename").notNull(),
    fileUrl: text("file_url"),
    fileSize: text("file_size"),
    totalPages: integer("total_pages"),
    status: text("status").default("processando").notNull(), // processando, concluido, erro
    coverage: integer("coverage"),
    createdAt: timestamp("created_at").defaultNow().notNull(),
  },
  (table) => [index("submission_projectId_idx").on(table.projectId)],
);

export const checkResult = pgTable(
  "check_result",
  {
    id: text("id").primaryKey(),
    submissionId: text("submission_id")
      .notNull()
      .references(() => submission.id, { onDelete: "cascade" }),
    requirementId: text("requirement_id")
      .notNull()
      .references(() => requirement.id, { onDelete: "cascade" }),
    status: text("status").notNull(), // 'atendido' | 'revisar' | 'faltando'
    feedback: text("feedback"),
    quote: text("quote"),
    pageNumber: integer("page_number"),
    createdAt: timestamp("created_at").defaultNow().notNull(),
  },
  (table) => [
    index("check_result_submissionId_idx").on(table.submissionId),
    index("check_result_requirementId_idx").on(table.requirementId),
  ],
);

export const projectRelations = relations(project, ({ one, many }) => ({
  user: one(user, {
    fields: [project.userId],
    references: [user.id],
  }),
  requirements: many(requirement),
  submissions: many(submission),
}));

export const requirementRelations = relations(requirement, ({ one, many }) => ({
  project: one(project, {
    fields: [requirement.projectId],
    references: [project.id],
  }),
  results: many(checkResult),
}));

export const submissionRelations = relations(submission, ({ one, many }) => ({
  project: one(project, {
    fields: [submission.projectId],
    references: [project.id],
  }),
  results: many(checkResult),
}));

export const checkResultRelations = relations(checkResult, ({ one }) => ({
  submission: one(submission, {
    fields: [checkResult.submissionId],
    references: [submission.id],
  }),
  requirement: one(requirement, {
    fields: [checkResult.requirementId],
    references: [requirement.id],
  }),
}));

