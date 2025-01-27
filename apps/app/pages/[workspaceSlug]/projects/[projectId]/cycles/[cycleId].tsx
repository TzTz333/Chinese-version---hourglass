import React, { useState } from "react";

import { useRouter } from "next/router";

import useSWR, { mutate } from "swr";
import { GetServerSidePropsContext } from "next";
// icons
import { ArrowLeftIcon } from "@heroicons/react/24/outline";
import { CyclesIcon } from "components/icons";
// lib
import { requiredAdmin, requiredAuth } from "lib/auth";
// layouts
import AppLayout from "layouts/app-layout";
// contexts
import { IssueViewContextProvider } from "contexts/issue-view.context";
// components
import { ExistingIssuesListModal, IssuesFilterView, IssuesView } from "components/core";
import { CycleDetailsSidebar } from "components/cycles";
// services
import issuesService from "services/issues.service";
import cycleServices from "services/cycles.service";
import projectService from "services/project.service";
// hooks
import useToast from "hooks/use-toast";
// ui
import { CustomMenu } from "components/ui";
import { BreadcrumbItem, Breadcrumbs } from "components/breadcrumbs";
// helpers
import { truncateText } from "helpers/string.helper";
import { getDateRangeStatus } from "helpers/date-time.helper";
// types
import { UserAuth } from "types";
// fetch-keys
import {
  CYCLE_ISSUES,
  CYCLE_LIST,
  PROJECT_DETAILS,
  CYCLE_DETAILS,
  PROJECT_ISSUES_LIST,
} from "constants/fetch-keys";

const SingleCycle: React.FC<UserAuth> = (props) => {
  const [cycleIssuesListModal, setCycleIssuesListModal] = useState(false);
  const [cycleSidebar, setCycleSidebar] = useState(true);

  const router = useRouter();
  const { workspaceSlug, projectId, cycleId } = router.query;

  const { setToastAlert } = useToast();

  const { data: activeProject } = useSWR(
    workspaceSlug && projectId ? PROJECT_DETAILS(projectId as string) : null,
    workspaceSlug && projectId
      ? () => projectService.getProject(workspaceSlug as string, projectId as string)
      : null
  );

  const { data: cycles } = useSWR(
    workspaceSlug && projectId ? CYCLE_LIST(projectId as string) : null,
    workspaceSlug && projectId
      ? () => cycleServices.getCycles(workspaceSlug as string, projectId as string)
      : null
  );

  const { data: cycleDetails } = useSWR(
    cycleId ? CYCLE_DETAILS(cycleId as string) : null,
    workspaceSlug && projectId && cycleId
      ? () =>
        cycleServices.getCycleDetails(
          workspaceSlug as string,
          projectId as string,
          cycleId as string
        )
      : null
  );

  const cycleStatus =
    cycleDetails?.start_date && cycleDetails?.end_date
      ? getDateRangeStatus(cycleDetails?.start_date, cycleDetails?.end_date)
      : "draft";

  const { data: issues } = useSWR(
    workspaceSlug && projectId
      ? PROJECT_ISSUES_LIST(workspaceSlug as string, projectId as string)
      : null,
    workspaceSlug && projectId
      ? () => issuesService.getIssues(workspaceSlug as string, projectId as string)
      : null
  );

  const openIssuesListModal = () => {
    setCycleIssuesListModal(true);
  };

  const handleAddIssuesToCycle = async (data: { issues: string[] }) => {
    if (!workspaceSlug || !projectId) return;

    await issuesService
      .addIssueToCycle(workspaceSlug as string, projectId as string, cycleId as string, data)
      .then(() => {
        mutate(CYCLE_ISSUES(cycleId as string));
      })
      .catch(() => {
        setToastAlert({
          type: "error",
          title: "Error!",
          message: "无法将选定的问题添加到循环中！请再试一次！",
        });
      });
  };

  return (
    <IssueViewContextProvider>
      <ExistingIssuesListModal
        isOpen={cycleIssuesListModal}
        handleClose={() => setCycleIssuesListModal(false)}
        issues={issues?.filter((i) => !i.cycle_id) ?? []}
        handleOnSubmit={handleAddIssuesToCycle}
      />
      <AppLayout
        memberType={props}
        breadcrumbs={
          <Breadcrumbs>
            <BreadcrumbItem
              title={`${activeProject?.name ?? "Project"} Cycles`}
              link={`/${workspaceSlug}/projects/${activeProject?.id}/cycles`}
            />
          </Breadcrumbs>
        }
        left={
          <CustomMenu
            label={
              <>
                <CyclesIcon className="h-3 w-3" />
                {cycleDetails?.name && truncateText(cycleDetails.name, 40)}
              </>
            }
            className="ml-1.5"
            width="auto"
          >
            {cycles?.map((cycle) => (
              <CustomMenu.MenuItem
                key={cycle.id}
                renderAs="a"
                href={`/${workspaceSlug}/projects/${activeProject?.id}/cycles/${cycle.id}`}
              >
                {truncateText(cycle.name, 40)}
              </CustomMenu.MenuItem>
            ))}
          </CustomMenu>
        }
        right={
          <div
            className={`flex items-center gap-2 ${cycleSidebar ? "mr-[24rem]" : ""} duration-300`}
          >
            <IssuesFilterView />
            <button
              type="button"
              className={`grid h-7 w-7 place-items-center rounded p-1 outline-none duration-300 hover:bg-gray-100 ${cycleSidebar ? "rotate-180" : ""
                }`}
              onClick={() => setCycleSidebar((prevData) => !prevData)}
            >
              <ArrowLeftIcon className="h-4 w-4" />
            </button>
          </div>
        }
      >
        <div className={`h-full ${cycleSidebar ? "mr-[24rem]" : ""} duration-300`}>
          <IssuesView
            type="cycle"
            userAuth={props}
            openIssuesListModal={openIssuesListModal}
            isCompleted={cycleStatus === "completed" ?? false}
          />
        </div>
        <CycleDetailsSidebar
          cycleStatus={cycleStatus}
          cycle={cycleDetails}
          isOpen={cycleSidebar}
          isCompleted={cycleStatus === "completed" ?? false}
        />
      </AppLayout>
    </IssueViewContextProvider>
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

export default SingleCycle;
