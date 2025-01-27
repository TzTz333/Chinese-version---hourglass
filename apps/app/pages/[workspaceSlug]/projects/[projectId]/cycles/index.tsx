import React, { useEffect, useState } from "react";

import { useRouter } from "next/router";
import dynamic from "next/dynamic";

import useSWR from "swr";

import { PlusIcon } from "@heroicons/react/24/outline";
import { Tab } from "@headlessui/react";
// lib
import { requiredAdmin, requiredAuth } from "lib/auth";

// services
import cycleService from "services/cycles.service";
import projectService from "services/project.service";

// layouts
import AppLayout from "layouts/app-layout";
// components
import { CompletedCyclesListProps, CreateUpdateCycleModal, CyclesList } from "components/cycles";
// ui
import { Loader, PrimaryButton } from "components/ui";
import { BreadcrumbItem, Breadcrumbs } from "components/breadcrumbs";
// icons
// types
import { SelectCycleType, UserAuth } from "types";
import type { NextPage, GetServerSidePropsContext } from "next";
// fetching keys
import {
  CYCLE_CURRENT_AND_UPCOMING_LIST,
  CYCLE_DRAFT_LIST,
  PROJECT_DETAILS,
} from "constants/fetch-keys";

const CompletedCyclesList = dynamic<CompletedCyclesListProps>(
  () => import("components/cycles").then((a) => a.CompletedCyclesList),
  {
    ssr: false,
    loading: () => (
      <Loader className="mb-5">
        <Loader.Item height="12rem" width="100%" />
      </Loader>
    ),
  }
);

const ProjectCycles: NextPage<UserAuth> = (props) => {
  const [selectedCycle, setSelectedCycle] = useState<SelectCycleType>();
  const [createUpdateCycleModal, setCreateUpdateCycleModal] = useState(false);

  const {
    query: { workspaceSlug, projectId },
  } = useRouter();

  const { data: activeProject } = useSWR(
    workspaceSlug && projectId ? PROJECT_DETAILS(projectId as string) : null,
    workspaceSlug && projectId
      ? () => projectService.getProject(workspaceSlug as string, projectId as string)
      : null
  );

  const { data: draftCycles } = useSWR(
    workspaceSlug && projectId ? CYCLE_DRAFT_LIST(projectId as string) : null,
    workspaceSlug && projectId
      ? () => cycleService.getDraftCycles(workspaceSlug as string, projectId as string)
      : null
  );

  const { data: currentAndUpcomingCycles } = useSWR(
    workspaceSlug && projectId ? CYCLE_CURRENT_AND_UPCOMING_LIST(projectId as string) : null,
    workspaceSlug && projectId
      ? () => cycleService.getCurrentAndUpcomingCycles(workspaceSlug as string, projectId as string)
      : null
  );

  useEffect(() => {
    if (createUpdateCycleModal) return;
    const timer = setTimeout(() => {
      setSelectedCycle(undefined);
      clearTimeout(timer);
    }, 500);
  }, [createUpdateCycleModal]);

  return (
    <AppLayout
      meta={{
        title: "Plane - Cycles",
      }}
      memberType={props}
      breadcrumbs={
        <Breadcrumbs>
          <BreadcrumbItem title="Projects" link={`/${workspaceSlug}/projects`} />
          <BreadcrumbItem title={`${activeProject?.name ?? "Project"} Cycles`} />
        </Breadcrumbs>
      }
      right={
        <PrimaryButton
          className="flex items-center gap-2"
          onClick={() => {
            const e = new KeyboardEvent("keydown", { key: "q" });
            document.dispatchEvent(e);
          }}
        >
          <PlusIcon className="w-4 h-4" />
          添加Cycle
        </PrimaryButton>
      }
    >
      <CreateUpdateCycleModal
        isOpen={createUpdateCycleModal}
        handleClose={() => setCreateUpdateCycleModal(false)}
        data={selectedCycle}
      />
      <div className="space-y-8">
        <div className="flex flex-col gap-5">
          {currentAndUpcomingCycles && currentAndUpcomingCycles.current_cycle.length > 0 && (
            <h3 className="text-3xl font-semibold text-black">当前的Cycle</h3>
          )}
          <div className="space-y-5">
            <CyclesList
              cycles={currentAndUpcomingCycles?.current_cycle}
              setCreateUpdateCycleModal={setCreateUpdateCycleModal}
              setSelectedCycle={setSelectedCycle}
              type="current"
            />
          </div>
        </div>
        <div className="flex flex-col gap-5">
          <h3 className="text-3xl font-semibold text-black">其他的Cycles</h3>
          <div>
            <Tab.Group>
              <Tab.List
                as="div"
                className="flex items-center justify-start gap-4 text-base font-medium"
              >
                <Tab
                  className={({ selected }) =>
                    `rounded-3xl border px-5 py-1.5 text-sm outline-none sm:px-7 sm:py-2 sm:text-base ${
                      selected
                        ? "border-theme bg-theme text-white"
                        : "border-gray-300 bg-white hover:bg-hover-gray"
                    }`
                  }
                >
                  将要进行
                </Tab>
                <Tab
                  className={({ selected }) =>
                    `rounded-3xl border px-5 py-1.5 text-sm outline-none sm:px-7 sm:py-2 sm:text-base ${
                      selected
                        ? "border-theme bg-theme text-white"
                        : "border-gray-300 bg-white hover:bg-hover-gray"
                    }`
                  }
                >
                  已完成
                </Tab>
                <Tab
                  className={({ selected }) =>
                    `rounded-3xl border px-5 py-1.5 text-sm outline-none sm:px-7 sm:py-2 sm:text-base ${
                      selected
                        ? "border-theme bg-theme text-white"
                        : "border-gray-300 bg-white hover:bg-hover-gray"
                    }`
                  }
                >
                  草稿
                </Tab>
              </Tab.List>
              <Tab.Panels>
                <Tab.Panel as="div" className="mt-8 space-y-5">
                  <CyclesList
                    cycles={currentAndUpcomingCycles?.upcoming_cycle}
                    setCreateUpdateCycleModal={setCreateUpdateCycleModal}
                    setSelectedCycle={setSelectedCycle}
                    type="upcoming"
                  />
                </Tab.Panel>
                <Tab.Panel as="div" className="mt-8 space-y-5">
                  <CompletedCyclesList
                    setCreateUpdateCycleModal={setCreateUpdateCycleModal}
                    setSelectedCycle={setSelectedCycle}
                  />
                </Tab.Panel>
                <Tab.Panel as="div" className="mt-8 space-y-5">
                  <CyclesList
                    cycles={draftCycles?.draft_cycles}
                    setCreateUpdateCycleModal={setCreateUpdateCycleModal}
                    setSelectedCycle={setSelectedCycle}
                    type="draft"
                  />
                </Tab.Panel>
              </Tab.Panels>
            </Tab.Group>
          </div>
        </div>
      </div>
    </AppLayout>
  );
};

export const getServerSideProps = async (ctx: GetServerSidePropsContext) => {
  const user = await requiredAuth(ctx.req?.headers.cookie);

  const redirectAfterSignIn = ctx.resolvedUrl;

  if (!user) {
    return {
      redirect: {
        destination: `/signin?next=${redirectAfterSignIn}`,
        permanent: false,
      },
    };
  }

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

export default ProjectCycles;
