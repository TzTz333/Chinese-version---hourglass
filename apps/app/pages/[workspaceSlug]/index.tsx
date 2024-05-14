import React, { useEffect, useState } from "react";

import { useRouter } from "next/router";

import useSWR, { mutate } from "swr";

// lib
import { requiredAuth } from "lib/auth";
// layouts
import AppLayout from "layouts/app-layout";
// services
import userService from "services/user.service";
// components
import {
  CompletedIssuesGraph,
  IssuesList,
  IssuesPieChart,
  IssuesStats,
} from "components/workspace";
// types
import type { NextPage, GetServerSidePropsContext } from "next";
// fetch-keys
import { USER_WORKSPACE_DASHBOARD } from "constants/fetch-keys";

/**
 * 页面组件：工作区页面
 */
const WorkspacePage: NextPage = () => {
  const [month, setMonth] = useState(new Date().getMonth() + 1);

  const router = useRouter();
  const { workspaceSlug } = router.query;

  const { data: workspaceDashboardData } = useSWR(
    workspaceSlug ? USER_WORKSPACE_DASHBOARD(workspaceSlug as string) : null,
    workspaceSlug ? () => userService.userWorkspaceDashboard(workspaceSlug as string, month) : null
  );

  useEffect(() => {
    mutate(USER_WORKSPACE_DASHBOARD(workspaceSlug as string));
  }, [month, workspaceSlug]);

  return (
    <AppLayout noHeader={true}>
      <div className="h-full w-full">
        <div className="flex flex-col gap-8">
          <IssuesStats data={workspaceDashboardData} />
          <div className="grid grid-cols-1 gap-8 lg:grid-cols-2">
            <IssuesList issues={workspaceDashboardData?.overdue_issues} type="overdue" />
            <IssuesList issues={workspaceDashboardData?.upcoming_issues} type="upcoming" />
            <IssuesPieChart groupedIssues={workspaceDashboardData?.state_distribution} />
            <CompletedIssuesGraph
              issues={workspaceDashboardData?.completed_issues}
              month={month}
              setMonth={setMonth}
            />
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

  return {
    props: {
      user,
    },
  };
};

export default WorkspacePage;
