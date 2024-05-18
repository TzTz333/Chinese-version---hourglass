import { useRouter } from "next/router";

import useSWR from "swr";

// headless ui
import { Disclosure, Transition } from "@headlessui/react";
// services
import issuesService from "services/issues.service";
import projectService from "services/project.service";
// hooks
import useIssuesProperties from "hooks/use-issue-properties";
// components
import { SingleListIssue } from "components/core";
// ui
import { Avatar, CustomMenu } from "components/ui";
// icons
import { PlusIcon } from "@heroicons/react/24/outline";
import { getPriorityIcon, getStateGroupIcon } from "components/icons";
// helpers
import { addSpaceIfCamelCase } from "helpers/string.helper";
// types
import { IIssue, IIssueLabels, IState, TIssueGroupByOptions, UserAuth } from "types";
// fetch-keys
import { PROJECT_ISSUE_LABELS, PROJECT_MEMBERS } from "constants/fetch-keys";

type Props = {
  type?: "issue" | "cycle" | "module";
  currentState?: IState | null;
  bgColor?: string;
  groupTitle: string;
  groupedByIssues: {
    [key: string]: IIssue[];
  };
  selectedGroup: TIssueGroupByOptions;
  addIssueToState: () => void;
  makeIssueCopy: (issue: IIssue) => void;
  handleEditIssue: (issue: IIssue) => void;
  handleDeleteIssue: (issue: IIssue) => void;
  openIssuesListModal?: (() => void) | null;
  removeIssue: ((bridgeId: string) => void) | null;
  isCompleted?: boolean;
  userAuth: UserAuth;
};

type StateToChineseMap = { [key: string]: string };
const stateNameToChinese: StateToChineseMap = {
  Backlog: '待办事项',
  Todo: "未开始",
  "In Progress": "进行中",
  Done: "已完成",
  Cancelled: "已取消",
};

const stateNameToChinese2: StateToChineseMap = {
  urgent: '紧急',
  high: "较高",
  medium: "中等",
  low: "较低",
  None: "None",
};

export const SingleList: React.FC<Props> = ({
  type,
  currentState,
  bgColor,
  groupTitle,
  groupedByIssues,
  selectedGroup,
  addIssueToState,
  makeIssueCopy,
  handleEditIssue,
  handleDeleteIssue,
  openIssuesListModal,
  removeIssue,
  isCompleted = false,
  userAuth,
}) => {
  const router = useRouter();
  const { workspaceSlug, projectId } = router.query;

  const [properties] = useIssuesProperties(workspaceSlug as string, projectId as string);

  const { data: issueLabels } = useSWR<IIssueLabels[]>(
    workspaceSlug && projectId ? PROJECT_ISSUE_LABELS(projectId as string) : null,
    workspaceSlug && projectId
      ? () => issuesService.getIssueLabels(workspaceSlug as string, projectId as string)
      : null
  );

  const { data: members } = useSWR(
    workspaceSlug && projectId ? PROJECT_MEMBERS(projectId as string) : null,
    workspaceSlug && projectId
      ? () => projectService.projectMembers(workspaceSlug as string, projectId as string)
      : null
  );

  const getGroupTitle = () => {
    let title = addSpaceIfCamelCase(groupTitle);

    switch (selectedGroup) {
      case "state":
        const stateName: string = addSpaceIfCamelCase(currentState?.name ?? "");
        title = stateNameToChinese[stateName];
        break;
      case "labels":
        title = issueLabels?.find((label) => label.id === groupTitle)?.name ?? "未定义标签";
        break;
      case "created_by":
        const member = members?.find((member) => member.member.id === groupTitle)?.member;
        title =
          member?.first_name && member.first_name !== ""
            ? `${member.first_name} ${member.last_name}`
            : member?.email ?? "";
        break;
      case "priority":
        const stateName2: string = title;
        title = stateNameToChinese2[stateName2];
        break;
    }
    // console.log("原始", title);



    return title;
  };
  // const title = getGroupTitle();
  // console.log(title);



  const getGroupIcon = () => {
    let icon;

    switch (selectedGroup) {
      case "state":
        icon = currentState && getStateGroupIcon(currentState.group, "18", "18", bgColor);
        break;
      case "priority":
        icon = getPriorityIcon(groupTitle, "h-[18px] w-[18px] flex items-center");
        break;
      case "labels":
        const labelColor =
          issueLabels?.find((label) => label.id === groupTitle)?.color ?? "#000000";
        icon = (
          <span
            className="h-[18px] w-[18px] flex-shrink-0 rounded-full"
            style={{ backgroundColor: labelColor }}
          />
        );
        break;
      case "created_by":
        const member = members?.find((member) => member.member.id === groupTitle)?.member;
        icon = <Avatar user={member} height="24px" width="24px" fontSize="12px" />;

        break;
    }

    return icon;
  };

  return (
    <Disclosure key={groupTitle} as="div" defaultOpen>
      {({ open }) => (
        <div className="rounded-[10px] border border-gray-300 bg-white">
          <div
            className={`flex items-center justify-between bg-gray-100 px-5 py-3 ${open ? "rounded-t-[10px]" : "rounded-[10px]"
              }`}
          >
            <Disclosure.Button>
              <div className="flex items-center gap-x-3">
                {selectedGroup !== null && (
                  <span className="flex items-center">{getGroupIcon()}</span>
                )}
                {selectedGroup !== null ? (
                  <h2 className="text-base font-semibold capitalize leading-6 text-gray-800">
                    {getGroupTitle()}
                  </h2>
                ) : (
                  <h2 className="font-medium leading-5">全部 Issues</h2>
                )}
                <span className="rounded-full bg-gray-200 py-0.5 px-3 text-sm text-black">
                  {groupedByIssues[groupTitle as keyof IIssue].length}
                </span>
              </div>
            </Disclosure.Button>
            {type === "issue" ? (
              <button
                type="button"
                className="p-1  text-gray-500 hover:bg-gray-100"
                onClick={addIssueToState}
              >
                <PlusIcon className="h-4 w-4" />
              </button>
            ) : isCompleted ? (
              ""
            ) : (
              <CustomMenu
                customButton={
                  <div className="flex items-center cursor-pointer">
                    <PlusIcon className="h-4 w-4" />
                  </div>
                }
                optionsPosition="right"
                noBorder
              >
                <CustomMenu.MenuItem onClick={addIssueToState}>新建</CustomMenu.MenuItem>
                {openIssuesListModal && (
                  <CustomMenu.MenuItem onClick={openIssuesListModal}>
                    添加 issue
                  </CustomMenu.MenuItem>
                )}
              </CustomMenu>
            )}
          </div>
          <Transition
            show={open}
            enter="transition duration-100 ease-out"
            enterFrom="transform opacity-0"
            enterTo="transform opacity-100"
            leave="transition duration-75 ease-out"
            leaveFrom="transform opacity-100"
            leaveTo="transform opacity-0"
          >
            <Disclosure.Panel>
              {groupedByIssues[groupTitle] ? (
                groupedByIssues[groupTitle].length > 0 ? (
                  groupedByIssues[groupTitle].map((issue, index) => (
                    <SingleListIssue
                      key={issue.id}
                      type={type}
                      issue={issue}
                      properties={properties}
                      groupTitle={groupTitle}
                      index={index}
                      editIssue={() => handleEditIssue(issue)}
                      makeIssueCopy={() => makeIssueCopy(issue)}
                      handleDeleteIssue={handleDeleteIssue}
                      removeIssue={() => {
                        if (removeIssue !== null && issue.bridge_id) removeIssue(issue.bridge_id);
                      }}
                      isCompleted={isCompleted}
                      userAuth={userAuth}
                    />
                  ))
                ) : (
                  <p className="px-4 py-3 text-sm text-gray-500">没有 issues</p>
                )
              ) : (
                <div className="flex h-full w-full items-center justify-center">加载中...</div>
              )}
            </Disclosure.Panel>
          </Transition>
        </div>
      )}
    </Disclosure>
  );
};
