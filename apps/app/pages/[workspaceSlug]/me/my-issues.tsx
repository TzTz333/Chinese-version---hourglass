import React from "react";
import { useRouter } from "next/router";

// headless ui
import { Disclosure, Popover, Transition } from "@headlessui/react";
// icons
import { ChevronDownIcon, PlusIcon, RectangleStackIcon } from "@heroicons/react/24/outline";
// layouts
import AppLayout from "layouts/app-layout";
// hooks
import useIssues from "hooks/use-issues";
// ui
import { Spinner, EmptySpace, EmptySpaceItem, PrimaryButton } from "components/ui";
import { Breadcrumbs, BreadcrumbItem } from "components/breadcrumbs";
// hooks
import useIssuesProperties from "hooks/use-issue-properties";
// types
import { IIssue, Properties } from "types";
// components
import { MyIssuesListItem } from "components/issues";
// helpers
import { replaceUnderscoreIfSnakeCase } from "helpers/string.helper";
// types
import type { NextPage } from "next";

const MyIssuesPage: NextPage = () => {
  const router = useRouter();
  const { workspaceSlug } = router.query;

  // fetching user issues
  const { myIssues } = useIssues(workspaceSlug as string);

  const [properties, setProperties] = useIssuesProperties(
    workspaceSlug ? (workspaceSlug as string) : undefined,
    undefined
  );
  const translatePropertyKey = (key) => {
    const translations = {
      "assignee": "责任人",
      "due_date": "截止日期",
      "key": "ID",
      "labels": "标签",
      "priority": "优先级",
      "state": "状态",
      "sub_issue_count": "下一级issue数量",
    };

    return translations[key] || key; // 如果没有翻译，则返回原键值
  };

  return (
    <>
      <AppLayout
        breadcrumbs={
          <Breadcrumbs>
            <BreadcrumbItem title="My Issues" />
          </Breadcrumbs>
        }
        right={
          <div className="flex items-center gap-2">
            {myIssues && myIssues.length > 0 && (
              <Popover className="relative">
                {({ open }) => (
                  <>
                    <Popover.Button
                      className={`group flex items-center gap-2 rounded-md border bg-transparent p-2 text-xs font-medium hover:bg-gray-100 hover:text-gray-900 focus:outline-none ${open ? "bg-gray-100 text-gray-900" : "text-gray-500"
                        }`}
                    >
                      <span>选择查看的属性</span>
                      <ChevronDownIcon className="h-4 w-4" aria-hidden="true" />
                    </Popover.Button>

                    <Transition
                      as={React.Fragment}
                      enter="transition ease-out duration-200"
                      enterFrom="opacity-0 translate-y-1"
                      enterTo="opacity-100 translate-y-0"
                      leave="transition ease-in duration-150"
                      leaveFrom="opacity-100 translate-y-0"
                      leaveTo="opacity-0 translate-y-1"
                    >
                      <Popover.Panel className="absolute right-1/2 z-10 mr-5 mt-1 w-screen max-w-xs translate-x-1/2 transform overflow-hidden rounded-lg bg-white p-3 shadow-lg">
                        <div className="relative flex flex-col gap-1 gap-y-4">
                          <div className="relative flex flex-col gap-1">
                            <h4 className="text-base text-gray-600">属性</h4>
                            <div className="flex flex-wrap items-center gap-2">
                              {Object.keys(properties).map((key) => (
                                <button
                                  key={key}
                                  type="button"
                                  className={`rounded border border-theme px-2 py-1 text-xs capitalize ${properties[key as keyof Properties]
                                      ? "border-theme bg-theme text-white"
                                      : ""
                                    }`}
                                  onClick={() => setProperties(key as keyof Properties)}
                                >
                                  {translatePropertyKey(key)}
                                  {/* {key === "key" ? "ID" : replaceUnderscoreIfSnakeCase(key)} */}

                                </button>
                              ))}
                            </div>
                          </div>
                        </div>
                      </Popover.Panel>
                    </Transition>
                  </>
                )}
              </Popover>
            )}
            <PrimaryButton
              className="flex items-center gap-2"
              onClick={() => {
                const e = new KeyboardEvent("keydown", { key: "c" });
                document.dispatchEvent(e);
              }}
            >
              <PlusIcon className="w-4 h-4" />
              添加Issue
            </PrimaryButton>
          </div>
        }
      >
        <div className="flex h-full w-full flex-col space-y-5">
          {myIssues ? (
            <>
              {myIssues.length > 0 ? (
                <div className="flex flex-col space-y-5">
                  <Disclosure as="div" defaultOpen>
                    {({ open }) => (
                      <div className="rounded-[10px] border border-gray-300 bg-white">
                        <div
                          className={`flex items-center justify-start bg-gray-100 px-5 py-3 ${open ? "rounded-t-[10px]" : "rounded-[10px]"
                            }`}
                        >
                          <Disclosure.Button>
                            <div className="flex items-center gap-x-2">
                              <span>
                                <ChevronDownIcon
                                  className={`h-4 w-4 text-gray-500 ${!open ? "-rotate-90 transform" : ""
                                    }`}
                                />
                              </span>
                              <h2 className="font-medium leading-5">我的Issues</h2>
                              <span className="rounded-full bg-gray-200 py-0.5 px-3 text-sm text-black">
                                {myIssues.length}
                              </span>
                            </div>
                          </Disclosure.Button>
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
                            {myIssues.map((issue: IIssue) => (
                              <MyIssuesListItem
                                key={issue.id}
                                issue={issue}
                                properties={properties}
                                projectId={issue.project}
                              />
                            ))}
                          </Disclosure.Panel>
                        </Transition>
                      </div>
                    )}
                  </Disclosure>
                </div>
              ) : (
                <div className="flex h-full w-full flex-col items-center justify-center px-4">
                  <EmptySpace
                    title="您尚未被分配任何Issue。"
                    description="Issue帮助您跟踪每一项工作。通过Issue，可以持续追踪正在发生什么、谁在处理它，以及完成了哪些工作。"
                    Icon={RectangleStackIcon}
                  >
                    <EmptySpaceItem
                      title="创建一个新的Issue"
                      description={
                        <span>
                          使用快捷键 <pre className="inline rounded bg-gray-200 px-2 py-1">C</pre> 创造一个新的Issue
                        </span>
                      }
                      Icon={PlusIcon}
                      action={() => {
                        const e = new KeyboardEvent("keydown", {
                          key: "c",
                        });
                        document.dispatchEvent(e);
                      }}
                    />
                  </EmptySpace>
                </div>
              )}
            </>
          ) : (
            <div className="flex h-full w-full items-center justify-center">
              <Spinner />
            </div>
          )}
        </div>
      </AppLayout>
    </>
  );
};

export default MyIssuesPage;
