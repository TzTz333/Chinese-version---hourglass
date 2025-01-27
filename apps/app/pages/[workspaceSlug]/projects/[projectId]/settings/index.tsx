import { useEffect, useState } from "react";

import { useRouter } from "next/router";

import useSWR, { mutate } from "swr";

// react-hook-form
import { Controller, useForm } from "react-hook-form";
import { IProject, IWorkspace, UserAuth } from "types";
// lib
import { requiredAdmin } from "lib/auth";
// layouts
import AppLayout from "layouts/app-layout";
// services
import projectService from "services/project.service";
// components
import { DeleteProjectModal } from "components/project";
import EmojiIconPicker from "components/emoji-icon-picker";
// hooks
import useToast from "hooks/use-toast";
// ui
import {
  Input,
  TextArea,
  Loader,
  CustomSelect,
  OutlineButton,
  SecondaryButton,
} from "components/ui";
import { BreadcrumbItem, Breadcrumbs } from "components/breadcrumbs";
// types
import type { NextPage, GetServerSidePropsContext } from "next";
// fetch-keys
import { PROJECTS_LIST, PROJECT_DETAILS } from "constants/fetch-keys";
// constants
import { NETWORK_CHOICES } from "constants/project";

const defaultValues: Partial<IProject> = {
  name: "",
  description: "",
  identifier: "",
  network: 0,
};

const GeneralSettings: NextPage<UserAuth> = ({ isMember, isOwner, isViewer, isGuest }) => {
  const [selectProject, setSelectedProject] = useState<string | null>(null);

  const { setToastAlert } = useToast();

  const router = useRouter();
  const { workspaceSlug, projectId } = router.query;

  const { data: projectDetails } = useSWR<IProject>(
    workspaceSlug && projectId ? PROJECT_DETAILS(projectId as string) : null,
    workspaceSlug && projectId
      ? () => projectService.getProject(workspaceSlug as string, projectId as string)
      : null
  );

  const {
    register,
    handleSubmit,
    reset,
    control,
    setError,
    formState: { errors, isSubmitting },
  } = useForm<IProject>({
    defaultValues,
  });

  useEffect(() => {
    if (projectDetails)
      reset({
        ...projectDetails,
        default_assignee: projectDetails.default_assignee?.id,
        project_lead: projectDetails.project_lead?.id,
        workspace: (projectDetails.workspace as IWorkspace).id,
      });
  }, [projectDetails, reset]);

  const updateProject = async (payload: Partial<IProject>) => {
    if (!workspaceSlug || !projectDetails) return;

    await projectService
      .updateProject(workspaceSlug as string, projectDetails.id, payload)
      .then((res) => {
        mutate<IProject>(
          PROJECT_DETAILS(projectDetails.id),
          (prevData) => ({ ...prevData, ...res }),
          false
        );
        mutate(PROJECTS_LIST(workspaceSlug as string));
        setToastAlert({
          type: "success",
          title: "Success!",
          message: "Project updated successfully",
        });
      })
      .catch(() => {
        setToastAlert({
          type: "error",
          title: "Error!",
          message: "Project could not be updated. Please try again.",
        });
      });
  };

  const onSubmit = async (formData: IProject) => {
    if (!workspaceSlug || !projectDetails) return;

    const payload: Partial<IProject> = {
      name: formData.name,
      network: formData.network,
      identifier: formData.identifier,
      description: formData.description,
      default_assignee: formData.default_assignee,
      project_lead: formData.project_lead,
      icon: formData.icon,
    };

    if (projectDetails.identifier !== formData.identifier)
      await projectService
        .checkProjectIdentifierAvailability(workspaceSlug as string, payload.identifier ?? "")
        .then(async (res) => {
          if (res.exists) setError("identifier", { message: "Identifier already exists" });
          else await updateProject(payload);
        });
    else await updateProject(payload);
  };

  return (
    <AppLayout
      memberType={{ isMember, isOwner, isViewer, isGuest }}
      breadcrumbs={
        <Breadcrumbs>
          <BreadcrumbItem
            title={`${projectDetails?.name ?? "Project"}`}
            link={`/${workspaceSlug}/projects/${projectDetails?.id}/issues`}
          />
          <BreadcrumbItem title="General Settings" />
        </Breadcrumbs>
      }
      settingsLayout
    >
      <DeleteProjectModal
        data={projectDetails ?? null}
        isOpen={Boolean(selectProject)}
        onClose={() => setSelectedProject(null)}
        onSuccess={() => {
          router.push(`/${workspaceSlug}/projects`);
        }}
      />
      <form onSubmit={handleSubmit(onSubmit)}>
        <div className="space-y-8 sm:space-y-12">
          <div className="grid grid-cols-12 items-start gap-4 sm:gap-16">
            <div className="col-span-12 sm:col-span-6">
              <h4 className="text-xl font-semibold">图标 & 项目名</h4>
              <p className="text-gray-500">为你的项目命名并选择一个图标。</p>
            </div>
            <div className="col-span-12 flex gap-2 sm:col-span-6">
              {projectDetails ? (
                <Controller
                  control={control}
                  name="icon"
                  render={({ field: { value, onChange } }) => (
                    <EmojiIconPicker
                      label={value ? String.fromCodePoint(parseInt(value)) : "Icon"}
                      value={value}
                      onChange={onChange}
                    />
                  )}
                />
              ) : (
                <Loader>
                  <Loader.Item height="46px" width="46px" light />
                </Loader>
              )}
              {projectDetails ? (
                <Input
                  id="name"
                  name="name"
                  error={errors.name}
                  register={register}
                  placeholder="Project Name"
                  validations={{
                    required: "Name is required",
                  }}
                />
              ) : (
                <Loader>
                  <Loader.Item height="46px" width="225px" light />
                </Loader>
              )}
            </div>
          </div>
          <div className="grid grid-cols-12 gap-4 sm:gap-16">
            <div className="col-span-12 sm:col-span-6">
              <h4 className="text-xl font-semibold">项目介绍</h4>
              <p className="text-gray-500">为你的项目添加一些介绍。</p>
            </div>
            <div className="col-span-12 sm:col-span-6">
              {projectDetails ? (
                <TextArea
                  id="description"
                  name="description"
                  error={errors.description}
                  register={register}
                  placeholder="Enter project description"
                  validations={{}}
                  className="min-h-[46px]"
                />
              ) : (
                <Loader className="w-full">
                  <Loader.Item height="46px" width="full" light />
                </Loader>
              )}
            </div>
          </div>
          <div className="grid grid-cols-12 gap-4 sm:gap-16">
            <div className="col-span-12 sm:col-span-6">
              <h4 className="text-xl font-semibold">标识符</h4>
              <p className="text-gray-500">
                为项目创建一个 1-6 个字符的标识符。
              </p>
            </div>
            <div className="col-span-12 sm:col-span-6">
              {projectDetails ? (
                <Input
                  id="identifier"
                  name="identifier"
                  error={errors.identifier}
                  register={register}
                  placeholder="Enter identifier"
                  validations={{
                    required: "Identifier is required",
                    minLength: {
                      value: 1,
                      message: "Identifier must at least be of 1 character",
                    },
                    maxLength: {
                      value: 9,
                      message: "Identifier must at most be of 9 characters",
                    },
                  }}
                />
              ) : (
                <Loader>
                  <Loader.Item height="46px" width="160px" light />
                </Loader>
              )}
            </div>
          </div>
          <div className="grid grid-cols-12 gap-4 sm:gap-16">
            <div className="col-span-12 sm:col-span-6">
              <h4 className="text-xl font-semibold">项目类型</h4>
              <p className="text-gray-500">选择项目类型是私人的or公开的。</p>
            </div>
            <div className="col-span-12 sm:col-span-6">
              {projectDetails ? (
                <Controller
                  name="network"
                  control={control}
                  render={({ field: { value, onChange } }) => (
                    <CustomSelect
                      value={value}
                      onChange={onChange}
                      label={
                        Object.keys(NETWORK_CHOICES).find((k) => k === value.toString())
                          ? NETWORK_CHOICES[value.toString() as keyof typeof NETWORK_CHOICES]
                          : "Select network"
                      }
                      input
                    >
                      {Object.keys(NETWORK_CHOICES).map((key) => (
                        <CustomSelect.Option key={key} value={parseInt(key)}>
                          {NETWORK_CHOICES[key as keyof typeof NETWORK_CHOICES]}
                        </CustomSelect.Option>
                      ))}
                    </CustomSelect>
                  )}
                />
              ) : (
                <Loader className="w-full">
                  <Loader.Item height="46px" width="160px" light />
                </Loader>
              )}
            </div>
          </div>
          <div>
            <div className="flex justify-end gap-2 sm:gap-4">
              <div className="flex gap-2 sm:gap-4">
                {projectDetails ? (
                  <div className="col-span-12 sm:col-span-6">
                    <OutlineButton
                      theme="danger"
                      onClick={() => setSelectedProject(projectDetails.id ?? null)}
                    >
                      删除项目
                    </OutlineButton>
                  </div>
                ) : (
                  <Loader className="mt-2 w-full">
                    <Loader.Item height="46px" width="100px" light />
                  </Loader>
                )}
                <div className="col-span-12 sm:col-span-6">
                  {projectDetails ? (
                    <SecondaryButton type="submit" loading={isSubmitting}>
                      {isSubmitting ? "更新项目中..." : "更新项目"}
                    </SecondaryButton>
                  ) : (
                    <Loader className="mt-2 w-full">
                      <Loader.Item height="34px" width="100px" light />
                    </Loader>
                  )}
                </div>
              </div>
            </div>
          </div>

        </div>
      </form>
    </AppLayout>
  );
};

export const getServerSideProps = async (ctx: GetServerSidePropsContext) => {
  const projectId = ctx.query.projectId as string;
  const workspaceSlug = ctx.query.workspaceSlug as string;

  const memberDetail = await requiredAdmin(workspaceSlug, projectId, ctx.req?.headers.cookie);

  return {
    props: {
      isOwner: memberDetail?.role === 20,
      isMember: memberDetail?.role === 15,
      isViewer: memberDetail?.role === 10,
      isGuest: memberDetail?.role === 5,
    },
  };
};

export default GeneralSettings;
