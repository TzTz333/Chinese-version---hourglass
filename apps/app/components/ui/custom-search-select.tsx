import React, { useState } from "react";
// 引入headless ui组件库中的Combobox和Transition组件
import { Combobox, Transition } from "@headlessui/react";
// 引入heroicons图标库中的几个图标
import { CheckIcon, ChevronDownIcon, MagnifyingGlassIcon } from "@heroicons/react/24/outline";

// 定义组件的属性类型
type CustomSearchSelectProps = {
  value: any; // 组件选中的值
  onChange: any; // 值变化时的回调函数
  options: { // 下拉菜单的选项数组
    value: any; // 选项的值
    query: string; // 用于搜索匹配的字符串
    content: JSX.Element; // 选项的展示内容
  }[];
  label?: string | JSX.Element; // 下拉选择框的标签，可以是字符串或者JSX元素
  textAlignment?: "left" | "center" | "right"; // 文本对齐方式
  height?: "sm" | "md" | "rg" | "lg"; // 下拉菜单的高度
  position?: "right" | "left"; // 下拉菜单的位置
  noChevron?: boolean; // 是否显示下拉箭头
  customButton?: JSX.Element; // 自定义的下拉按钮
  optionsClassName?: string; // 下拉选项的自定义类名
  disabled?: boolean; // 组件是否禁用
  selfPositioned?: boolean; // 下拉菜单是否自定义定位
  multiple?: boolean; // 是否支持多选
  footerOption?: JSX.Element; // 下拉菜单底部的自定义内容
};

export const CustomSearchSelect = ({
  label,
  textAlignment,
  height = "md",
  value,
  onChange,
  options,
  position = "left",
  noChevron = false,
  customButton,
  optionsClassName = "",
  disabled = false,
  selfPositioned = false,
  multiple = false,
  footerOption,
}: CustomSearchSelectProps) => {
  const [query, setQuery] = useState(""); // 组件内部用于搜索的状态

  // 根据用户输入的搜索词过滤选项列表
  const filteredOptions = query === "" ? options : options.filter((option) => option.query.toLowerCase().includes(query.toLowerCase()));

  const props: any = {
    value,
    onChange,
    disabled,
  };

  // 如果支持多选，向props添加multiple属性
  if (multiple) props.multiple = true;

  // 组件渲染逻辑
  return (
    <Combobox
      as="div"
      className={`${!selfPositioned ? "relative" : ""} flex-shrink-0 text-left`}
      {...props}
    >
      {({ open }: any) => (
        <>
          {customButton ? ( // 如果有自定义按钮，则使用之
            <Combobox.Button as="div">{customButton}</Combobox.Button>
          ) : ( // 否则渲染默认按钮
            <Combobox.Button
              className={`flex w-full ${disabled ? "cursor-not-allowed" : "cursor-pointer hover:bg-gray-100"
                } items-center justify-between gap-1 rounded-md border px-3 py-1.5 text-xs shadow-sm duration-300 focus:border-indigo-500 focus:outline-none focus:ring-1 focus:ring-indigo-500 ${textAlignment === "right"
                  ? "text-right"
                  : textAlignment === "center"
                    ? "text-center"
                    : "text-left"
                }`}
            >
              {label}
              {!noChevron && !disabled && (
                <ChevronDownIcon className="h-3 w-3" aria-hidden="true" />
              )}
            </Combobox.Button>
          )}

          <Transition // 下拉菜单的过渡动画
            show={open}
            as={React.Fragment}
            enter="transition ease-out duration-200"
            enterFrom="opacity-0 translate-y-1"
            enterTo="opacity-100 translate-y-0"
            leave="transition ease-in duration-150"
            leaveFrom="opacity-100 translate-y-0"
            leaveTo="opacity-0 translate-y-1"
          >
            <Combobox.Options // 下拉选项列表
              className={`${optionsClassName} absolute min-w-[10rem] p-2 ${position === "right" ? "right-0" : "left-0"
                } z-10 mt-1 origin-top-right rounded-md bg-white text-xs shadow-lg ring-1 ring-black ring-opacity-5 focus:outline-none`}
            >
              <div className="flex w-full items-center justify-start rounded-sm border-[0.6px] bg-gray-100 px-2">
                <MagnifyingGlassIcon className="h-3 w-3 text-gray-500" />
                <Combobox.Input // 搜索输入框
                  className="w-full bg-transparent py-1 px-2 text-xs text-gray-500 focus:outline-none"
                  onChange={(e) => setQuery(e.target.value)}
                  placeholder="Type to search..."
                  displayValue={(assigned: any) => assigned?.name}
                />
              </div>
              <div // 下拉选项的容器
                className={`mt-2 space-y-1 ${height === "sm"
                  ? "max-h-28"
                  : height === "md"
                    ? "max-h-44"
                    : height === "rg"
                      ? "max-h-56"
                      : height === "lg"
                        ? "max-h-80"
                        : ""
                  } overflow-y-scroll`}
              >
                {filteredOptions ? ( // 根据搜索结果渲染选项
                  filteredOptions.length > 0 ? (
                    filteredOptions.map((option) => (
                      <Combobox.Option // 单个选项
                        key={option.value}
                        value={option.value}
                        className={({ active, selected }) =>
                          `${active || selected ? "bg-hover-gray" : ""} ${selected ? "font-medium" : ""
                          } flex cursor-pointer select-none items-center justify-between gap-2 truncate rounded px-1 py-1.5 text-gray-500`
                        }
                      >
                        {({ active, selected }) => (
                          <>
                            {/* 选项内容 */}
                            {option.content}
                            <div // 选中状态的勾选图标
                              className={`flex items-center justify-center rounded border border-gray-500 p-0.5 ${active || selected ? "opacity-100" : "opacity-0"
                                }`}
                            >
                              <CheckIcon
                                className={`h-3 w-3 ${selected ? "opacity-100" : "opacity-0"}`}
                              />
                            </div>
                          </>
                        )}
                      </Combobox.Option>
                    ))
                  ) : (
                    <p className="text-center text-gray-500">没有匹配结果</p> // 没有搜索结果时的提示
                  )
                ) : (
                  <p className="text-center text-gray-500">加载...</p> // 数据加载时的提示
                )}
              </div>
              {/* 下拉菜单底部的自定义内容 */}
              {footerOption}
            </Combobox.Options>
          </Transition>
        </>
      )}
    </Combobox>
  );
};