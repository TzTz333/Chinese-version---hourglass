import { useRouter } from "next/router";
import Link from "next/link";

// icons
import { ExclamationTriangleIcon } from "@heroicons/react/20/solid";
// helpers
import { renderShortDateWithYearFormat } from "helpers/date-time.helper";
import { truncateText } from "helpers/string.helper";
// types
import { IIssueLite } from "types";
import { Loader } from "components/ui";
import { LayerDiagonalIcon } from "components/icons";

type Props = {
  issues: IIssueLite[] | undefined;
  type: "overdue" | "upcoming";
};

export const IssuesList: React.FC<Props> = ({ issues, type }) => {
  //翻译函数
  const translateType = (type: string) => {
    const typesTranslation: { [key: string]: string } = {
      overdue: "逾期",
      upcoming: "待办",
    };

    return typesTranslation[type] || type;
  };

  const router = useRouter();
  const { workspaceSlug } = router.query;

  const getDateDifference = (date: Date) => {
    const today = new Date();

    let diffDays = 0;
    if (type === "overdue") {
      const diffTime = Math.abs(today.valueOf() - date.valueOf());
      diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
    } else return date.getDate() - today.getDate();

    return diffDays;
  };

  return (
    <div>
      <h3 className="mb-2 font-semibold capitalize">{translateType(type)}事项</h3>
      {issues ? (
        <div className="rounded-[10px] border bg-white p-4 text-sm h-[calc(100%-2.25rem)]">
          <div
            className={`mb-2 grid grid-cols-4 gap-2 rounded-lg px-3 py-2 font-medium ${type === "overdue" ? "bg-red-100" : "bg-gray-100"
              }`}
          >
            <h4 className="capitalize">{translateType(type)}</h4>
            <h4 className="col-span-2">Issue</h4>
            <h4>截止日期</h4>
          </div>
          <div className="max-h-72 overflow-y-scroll">
            {issues.length > 0 ? (
              issues.map((issue) => {
                const dateDifference = getDateDifference(new Date(issue.target_date as string));

                return (
                  <Link
                    href={`/${workspaceSlug}/projects/${issue.project_id}/issues/${issue.id}`}
                    key={issue.id}
                  >
                    <a>
                      <div className="grid grid-cols-4 gap-2 px-3 py-2">
                        <h5
                          className={`flex cursor-default items-center gap-2 ${type === "overdue"
                              ? dateDifference > 6
                                ? "text-red-500"
                                : "text-yellow-400"
                              : ""
                            }`}
                        >
                          {type === "overdue" && (
                            <ExclamationTriangleIcon className="h-3.5 w-3.5" />
                          )}
                          {dateDifference} {dateDifference > 1 ? "days" : "day"}
                        </h5>
                        <h5 className="col-span-2">{truncateText(issue.name, 30)}</h5>
                        <h5 className="cursor-default">
                          {renderShortDateWithYearFormat(new Date(issue.target_date as string))}
                        </h5>
                      </div>
                    </a>
                  </Link>
                );
              })
            ) : (
              <div className="grid h-full place-items-center">
                <div className="flex flex-col items-center gap-4">
                  <LayerDiagonalIcon height={60} width={60} />
                  <span>
                    使用快捷键{" "}
                    <pre className="inline rounded bg-gray-200 px-2 py-1">C</pre> 创建新问题。
                  </span>
                </div>
              </div>
            )}
          </div>
        </div>
      ) : (
        <Loader>
          <Loader.Item height="200" />
        </Loader>
      )}
    </div>
  );
};
