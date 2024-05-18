// 分组选项的类型定义，用于问题(issue)的分组
export const GROUP_BY_OPTIONS: Array<{
  name: string; // 名称
  key: TIssueGroupByOptions; // 分组的键，对应于问题的某个属性
}> = [
    { name: "状态", key: "state" }, // 按状态分组
    { name: "优先级", key: "priority" }, // 按优先级分组
    { name: "标签", key: "labels" }, // 按标签分组
    { name: "创建人", key: "created_by" }, // 按创建人分组
    { name: "无", key: null }, // 无分组
  ];

// 排序选项的类型定义，用于问题(issue)的排序
export const ORDER_BY_OPTIONS: Array<{
  name: string; // 名称
  key: TIssueOrderByOptions; // 排序的键，对应于问题的某个属性
}> = [
    // { name: "手动", key: "sort_order" },
    { name: "最新创建", key: "-created_at" }, // 按创建时间降序
    { name: "最后更新", key: "updated_at" }, // 按更新时间升序
    { name: "优先级", key: "priority" }, // 按优先级排序
  ];

// 过滤选项的类型定义，用于问题(issue)的过滤
export const FILTER_ISSUE_OPTIONS: Array<{
  name: string; // 名称
  key: "active" | "backlog" | null; // 过滤的键
}> = [
    {
      name: "全部",
      key: null, // 不进行过滤
    },
    {
      name: "处理中的 Issues",
      key: "active", // 过滤出活跃的问题
    },
    {
      name: "待办的 Issues",
      key: "backlog", // 过滤出待办的问题
    },
  ];

// 引入类型定义文件
import { IIssue, TIssueGroupByOptions, TIssueOrderByOptions } from "types";

// 处理问题数据变动的函数类型定义
type THandleIssuesMutation = (
  // 函数参数
  formData: Partial<IIssue>, // 变动的问题数据
  oldGroupTitle: string, // 原分组标题
  selectedGroupBy: TIssueGroupByOptions, // 当前选择的分组选项
  issueIndex: number, // 问题在数组中的索引
  prevData?: // 原始数据
    | {
      [key: string]: IIssue[];
    }
    | IIssue[]
) =>
  | {
    [key: string]: IIssue[];
  }
  | IIssue[]
  | undefined;

// 实现处理问题数据变动的函数
export const handleIssuesMutation: THandleIssuesMutation = (
  formData,
  oldGroupTitle,
  selectedGroupBy,
  issueIndex,
  prevData
) => {
  // 如果没有原始数据，则直接返回
  if (!prevData) return prevData;

  // 如果原始数据是数组，则直接在数组中更新问题
  if (Array.isArray(prevData)) {
    // 创建更新后的问题
    const updatedIssue = {
      ...prevData[issueIndex], // 保留原有数据
      ...formData, // 应用变动数据
      // 如果formData中有assignees_list则使用，否则保留原有的assignees_list
      assignees: formData?.assignees_list ?? prevData[issueIndex]?.assignees_list,
    };

    // 更新数组中的问题
    prevData.splice(issueIndex, 1, updatedIssue);

    // 返回更新后的数组
    return [...prevData];
  } else {
    // 如果原始数据是对象，则更新对象中的问题
    // 获取原分组的问题数组
    const oldGroup = prevData[oldGroupTitle ?? ""] ?? [];

    let newGroup: IIssue[] = [];

    // 根据分组选项确定新分组的问题数组
    if (selectedGroupBy === "priority") newGroup = prevData[formData.priority ?? ""] ?? [];
    else if (selectedGroupBy === "state") newGroup = prevData[formData.state ?? ""] ?? [];

    // 创建更新后的问题
    const updatedIssue = {
      ...oldGroup[issueIndex], // 保留原有数据
      ...formData, // 应用变动数据
      // 如果formData中有assignees_list则使用，否则保留原有的assignees_list
      assignees: formData?.assignees_list ?? oldGroup[issueIndex]?.assignees_list,
    };

    // 在原分组中移除问题，在新分组中添加问题
    oldGroup.splice(issueIndex, 1);
    newGroup.push(updatedIssue);

    // 确定更新的分组
    const groupThatIsUpdated = selectedGroupBy === "priority" ? formData.priority : formData.state;

    // 返回更新后的对象
    return {
      ...prevData, // 保留其他分组不变
      [oldGroupTitle ?? ""]: oldGroup, // 更新原分组
      [groupThatIsUpdated ?? ""]: newGroup, // 更新新分组
    };
  }
};
