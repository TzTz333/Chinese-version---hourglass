import React from "react";
import { LinearProgressIndicator } from "components/ui";

export const EmptyCycle = () => {
  const emptyCycleData = [
    {
      id: 1,
      name: "待办",
      value: 20,
      color: "#DEE2E6",
    },
    {
      id: 2,
      name: "未开始",
      value: 14,
      color: "#26B5CE",
    },
    {
      id: 3,
      name: "已开始",
      value: 27,
      color: "#F7AE59",
    },
    {
      id: 4,
      name: "已取消",
      value: 15,
      color: "#D687FF",
    },
    {
      id: 5,
      name: "已完成",
      value: 14,
      color: "#09A953",
    },
  ];
  return (
    <div className="flex h-full w-full flex-col items-center justify-center gap-5 ">
      <div className="relative h-32 w-72">
        <div className="absolute right-0 top-0 flex w-64 flex-col rounded-[10px] bg-white text-xs shadow">
          <div className="flex flex-col items-start justify-center gap-2.5 p-3.5">
            <span className="text-sm font-semibold text-black">周期名称</span>
            <div className="flex h-full w-full items-center gap-4">
              <span className="h-2 w-20 rounded-full bg-gray-200" />
              <span className="h-2 w-20 rounded-full bg-gray-200" />
            </div>
          </div>

          <div className="border-t border-gray-200 bg-gray-100 px-4 py-3">
            <LinearProgressIndicator data={emptyCycleData} />
          </div>
        </div>

        <div className="absolute left-0 bottom-0 flex w-64 flex-col rounded-[10px] bg-white text-xs shadow">
          <div className="flex flex-col items-start justify-center gap-2.5 p-3.5">
            <span className="text-sm font-semibold text-black">周期名称</span>
            <div className="flex h-full w-full items-center gap-4">
              <span className="h-2 w-20 rounded-full bg-gray-200" />
              <span className="h-2 w-20 rounded-full bg-gray-200" />
            </div>
          </div>

          <div className="border-t border-gray-200 bg-gray-100 px-4 py-3">
            <LinearProgressIndicator data={emptyCycleData} />
          </div>
        </div>
      </div>

      <div className="flex flex-col items-center justify-center gap-4 text-center ">
        <h3 className="text-xl font-semibold">创建一个新的周期</h3>
        <p className="text-sm text-gray-500">
          通过将项目限定在固定的时间范围内 <br />
          使用周期进行更高效地推进 <br />
          立即创建新的周期!
        </p>
      </div>
    </div>
  );
};
