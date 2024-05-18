// 引入 React 钩子和上下文 API
import { createContext, useCallback, useEffect, useReducer } from "react";
// 引入 Next.js 的路由钩子
import { useRouter } from "next/router";
// 引入 SWR 库用于数据获取和状态管理
import useSWR, { mutate } from "swr";

// 引入组件
import ToastAlert from "components/toast-alert";
// 引入服务层，用于与后端 API 交互
import projectService from "services/project.service";
import viewsService from "services/views.service";
// 引入类型定义
import {
  IIssueFilterOptions,
  TIssueViewOptions,
  IProjectMember,
  TIssueGroupByOptions,
  TIssueOrderByOptions,
} from "types";
// 引入常量，用于定义 fetch 键
import { USER_PROJECT_VIEW, VIEW_DETAILS } from "constants/fetch-keys";
// 创建 issueView 上下文，用于在组件树中共享状态和函数
export const issueViewContext = createContext<ContextType>({} as ContextType);
// 定义状态类型和行为类型
type IssueViewProps = {
  issueView: TIssueViewOptions;
  groupByProperty: TIssueGroupByOptions;
  orderBy: TIssueOrderByOptions;
  showEmptyGroups: boolean;
  filters: IIssueFilterOptions;
};

type ReducerActionType = {
  type:
  | "REHYDRATE_THEME"
  | "SET_ISSUE_VIEW"
  | "SET_ORDER_BY_PROPERTY"
  | "SET_SHOW_EMPTY_STATES"
  | "SET_FILTERS"
  | "SET_GROUP_BY_PROPERTY"
  | "RESET_TO_DEFAULT";
  payload?: Partial<IssueViewProps>;
};

type ContextType = IssueViewProps & {
  setGroupByProperty: (property: TIssueGroupByOptions) => void;
  setOrderBy: (property: TIssueOrderByOptions) => void;
  setShowEmptyGroups: (property: boolean) => void;
  setFilters: (filters: Partial<IIssueFilterOptions>, saveToServer?: boolean) => void;
  resetFilterToDefault: () => void;
  setNewFilterDefaultView: () => void;
  setIssueView: (property: TIssueViewOptions) => void;
};

type StateType = {
  issueView: TIssueViewOptions;
  groupByProperty: TIssueGroupByOptions;
  orderBy: TIssueOrderByOptions;
  showEmptyGroups: boolean;
  filters: IIssueFilterOptions;
};
type ReducerFunctionType = (state: StateType, action: ReducerActionType) => StateType;

// 定义初始状态
export const initialState: StateType = {
  issueView: "list",
  groupByProperty: null,
  orderBy: "-created_at",
  showEmptyGroups: true,
  filters: {
    type: null,
    priority: null,
    assignees: null,
    labels: null,
    state: null,
    issue__assignees__id: null,
    issue__labels__id: null,
    created_by: null,
  },
};

// 定义状态管理的 reducer 函数
export const reducer: ReducerFunctionType = (state, action) => {
  const { type, payload } = action;

  switch (type) {
    case "REHYDRATE_THEME": {
      let collapsed: any = localStorage.getItem("collapsed");
      collapsed = collapsed ? JSON.parse(collapsed) : false;

      return { ...initialState, ...payload, collapsed };
    }

    case "SET_ISSUE_VIEW": {
      const newState = {
        ...state,
        issueView: payload?.issueView || "list",
      };

      return {
        ...state,
        ...newState,
      };
    }

    case "SET_GROUP_BY_PROPERTY": {
      const newState = {
        ...state,
        groupByProperty: payload?.groupByProperty || null,
      };

      return {
        ...state,
        ...newState,
      };
    }

    case "SET_ORDER_BY_PROPERTY": {
      const newState = {
        ...state,
        orderBy: payload?.orderBy || "-created_at",
      };

      return {
        ...state,
        ...newState,
      };
    }

    case "SET_SHOW_EMPTY_STATES": {
      const newState = {
        ...state,
        showEmptyGroups: payload?.showEmptyGroups || true,
      };

      return {
        ...state,
        ...newState,
      };
    }

    case "SET_FILTERS": {
      const newState = {
        ...state,
        filters: {
          ...state.filters,
          ...payload,
        },
      };

      return {
        ...state,
        ...newState,
      };
    }

    case "RESET_TO_DEFAULT": {
      return {
        ...initialState,
        ...payload,
      };
    }

    default: {
      return state;
    }
  }
};

// 定义用于保存数据到服务器的异步函数
const saveDataToServer = async (workspaceSlug: string, projectID: string, state: any) => {
  await projectService.setProjectView(workspaceSlug, projectID, {
    view_props: state,
  });
};

// 定义用于发送筛选数据到服务器的异步函数
const sendFilterDataToServer = async (
  workspaceSlug: string,
  projectId: string,
  viewId: string,
  state: any
) => {
  // 更新特定视图的筛选条件
  await viewsService.patchView(workspaceSlug, projectId, viewId, {
    ...state,
  });
};

// 定义用于设置新的默认视图的异步函数
const setNewDefault = async (workspaceSlug: string, projectId: string, state: any) => {
  // 使用 SWR 的 mutate 函数更新本地缓存的项目成员数据，无需重新请求
  mutate<IProjectMember>(
    workspaceSlug && projectId ? USER_PROJECT_VIEW(projectId as string) : null,
    (prevData) => {
      if (!prevData) return prevData;

      // 更新视图属性
      return {
        ...prevData,
        view_props: state,
      };
    },
    false
  );

  // 在服务器上设置新的默认视图属性
  await projectService.setProjectView(workspaceSlug, projectId, {
    view_props: state,
    default_props: state,
  });
};

// 定义 IssueViewContextProvider 组件，用于封装状态管理逻辑和提供上下文
export const IssueViewContextProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  // 使用 useReducer 管理状态
  const [state, dispatch] = useReducer(reducer, initialState);

  // 使用 useRouter 获取路由信息
  const router = useRouter();
  const { workspaceSlug, projectId, viewId } = router.query;

  const { data: myViewProps, mutate: mutateMyViewProps } = useSWR(
    workspaceSlug && projectId ? USER_PROJECT_VIEW(projectId as string) : null,
    workspaceSlug && projectId
      ? () => projectService.projectMemberMe(workspaceSlug as string, projectId as string)
      : null
  );

  const { data: viewDetails, mutate: mutateViewDetails } = useSWR(
    workspaceSlug && projectId && viewId ? VIEW_DETAILS(viewId as string) : null,
    workspaceSlug && projectId && viewId
      ? () =>
        viewsService.getViewDetails(
          workspaceSlug as string,
          projectId as string,
          viewId as string
        )
      : null
  );

  const setIssueView = useCallback(
    (property: TIssueViewOptions) => {
      dispatch({
        type: "SET_ISSUE_VIEW",
        payload: {
          issueView: property,
        },
      });

      if (property === "kanban") {
        dispatch({
          type: "SET_GROUP_BY_PROPERTY",
          payload: {
            groupByProperty: "state",
          },
        });
      }

      if (!workspaceSlug || !projectId) return;

      saveDataToServer(workspaceSlug as string, projectId as string, {
        ...state,
        issueView: property,
        groupByProperty: "state",
      });
    },
    [workspaceSlug, projectId, state]
  );

  const setGroupByProperty = useCallback(
    (property: TIssueGroupByOptions) => {
      dispatch({
        type: "SET_GROUP_BY_PROPERTY",
        payload: {
          groupByProperty: property,
        },
      });

      if (!workspaceSlug || !projectId) return;

      mutateMyViewProps((prevData) => {
        if (!prevData) return prevData;

        return {
          ...prevData,
          view_props: {
            ...state,
            groupByProperty: property,
          },
        };
      }, false);

      saveDataToServer(workspaceSlug as string, projectId as string, {
        ...state,
        groupByProperty: property,
      });
    },
    [projectId, workspaceSlug, state, mutateMyViewProps]
  );

  const setOrderBy = useCallback(
    (property: TIssueOrderByOptions) => {
      dispatch({
        type: "SET_ORDER_BY_PROPERTY",
        payload: {
          orderBy: property,
        },
      });

      if (!workspaceSlug || !projectId) return;

      mutateMyViewProps((prevData) => {
        if (!prevData) return prevData;

        return {
          ...prevData,
          view_props: {
            ...state,
            orderBy: property,
          },
        };
      }, false);

      saveDataToServer(workspaceSlug as string, projectId as string, {
        ...state,
        orderBy: property,
      });
    },
    [projectId, workspaceSlug, state, mutateMyViewProps]
  );

  const setShowEmptyGroups = useCallback(
    (property: boolean) => {
      dispatch({
        type: "SET_SHOW_EMPTY_STATES",
        payload: {
          showEmptyGroups: property,
        },
      });

      if (!workspaceSlug || !projectId) return;

      mutateMyViewProps((prevData) => {
        if (!prevData) return prevData;

        return {
          ...prevData,
          view_props: {
            ...state,
            showEmptyGroups: property,
          },
        };
      }, false);

      saveDataToServer(workspaceSlug as string, projectId as string, {
        ...state,
        showEmptyGroups: property,
      });
    },
    [projectId, workspaceSlug, state, mutateMyViewProps]
  );

  const setFilters = useCallback(
    (property: Partial<IIssueFilterOptions>, saveToServer = true) => {
      Object.keys(property).forEach((key) => {
        if (property[key as keyof typeof property]?.length === 0) {
          property[key as keyof typeof property] = null;
        }
      });

      dispatch({
        type: "SET_FILTERS",
        payload: {
          filters: {
            ...state.filters,
            ...property,
          },
        },
      });

      if (!workspaceSlug || !projectId) return;

      mutateMyViewProps((prevData) => {
        if (!prevData) return prevData;

        return {
          ...prevData,
          view_props: {
            ...state,
            filters: {
              ...state.filters,
              ...property,
            },
          },
        };
      }, false);

      if (viewId) {
        mutateViewDetails((prevData: any) => {
          if (!prevData) return prevData;
          return {
            ...prevData,
            query_data: {
              ...state.filters,
              ...property,
            },
          };
        }, false);
        if (saveToServer)
          sendFilterDataToServer(workspaceSlug as string, projectId as string, viewId as string, {
            query_data: {
              ...state.filters,
              ...property,
            },
          });
      } else if (saveToServer)
        saveDataToServer(workspaceSlug as string, projectId as string, {
          ...state,
          filters: {
            ...state.filters,
            ...property,
          },
        });
    },
    [projectId, workspaceSlug, state, mutateMyViewProps, viewId, mutateViewDetails]
  );

  const setNewDefaultView = useCallback(() => {
    if (!workspaceSlug || !projectId) return;

    setNewDefault(workspaceSlug as string, projectId as string, state).then(() => {
      mutateMyViewProps();
    });
  }, [projectId, workspaceSlug, state, mutateMyViewProps]);

  const resetToDefault = useCallback(() => {
    dispatch({
      type: "RESET_TO_DEFAULT",
      payload: myViewProps?.default_props,
    });

    if (!workspaceSlug || !projectId) return;

    saveDataToServer(workspaceSlug as string, projectId as string, myViewProps?.default_props);
  }, [projectId, workspaceSlug, myViewProps]);

  // 使用 React 的 useEffect 钩子根据从服务器获取的数据重新设置组件的状态
  useEffect(() => {
    // 使用 dispatch 方法发送一个 action 来更新状态
    dispatch({
      type: "REHYDRATE_THEME",
      payload: {
        ...myViewProps?.view_props,
        filters: {
          ...myViewProps?.view_props?.filters,
          ...viewDetails?.query_data,
        } as any,
      },
    });
  }, [myViewProps, viewDetails]);

  //返回 IssueViewContextProvider 组件，它通过 issueViewContext.Provider 提供上下文
  //这个上下文包含了所有的状态和操作状态的函数，以便在组件树的任何地方使用
  return (
    <issueViewContext.Provider
      value={{
        issueView: state.issueView,
        groupByProperty: state.groupByProperty,
        setGroupByProperty,
        orderBy: state.orderBy,
        showEmptyGroups: state.showEmptyGroups,
        setOrderBy,
        setShowEmptyGroups,
        filters: state.filters,
        setFilters,
        resetFilterToDefault: resetToDefault,
        setNewFilterDefaultView: setNewDefaultView,
        setIssueView,
      }}
    >
      {/* 渲染 ToastAlert 组件用于显示通知 */}
      <ToastAlert />
      {/* 渲染所有子组件 */}
      {children}
    </issueViewContext.Provider>
  );
};
