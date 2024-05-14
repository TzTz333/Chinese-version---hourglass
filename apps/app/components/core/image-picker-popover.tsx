// 导入 React 及其相关钩子
import React, { useEffect, useState, useRef } from "react";

// 导入 Next.js 的 Image 组件用于图片优化
import Image from "next/image";

// 使用 SWR 进行数据获取和缓存
import useSWR from "swr";

// 导入 Headless UI 组件库中的 Tab，Transition 和 Popover 组件
import { Tab, Transition, Popover } from "@headlessui/react";

// 导入服务层，这里假设 fileService 提供图片获取等功能
import fileService from "services/file.service";

// 导入 UI 组件，这里包括输入框 Input，加载动画 Spinner 和主按钮 PrimaryButton
import { Input, Spinner, PrimaryButton } from "components/ui";
// 导入自定义钩子用于检测点击组件外部事件
import useOutsideClickDetector from "hooks/use-outside-click-detector";

// Tab 选项配置，定义两个选项卡：Unsplash 图片和上传图片
const tabOptions = [
  {
    key: "unsplash",
    title: "Unsplash",
  },
  {
    key: "upload",
    title: "Upload",
  },
];

// 定义组件的 Props 类型
type Props = {
  label: string | React.ReactNode; // 显示标签，可以是字符串或 React 节点
  value: string | null; // 当前选择的图片 URL 或 null
  onChange: (data: string) => void; // 图片 URL 改变时的回调函数
};

export const ImagePickerPopover: React.FC<Props> = ({ label, value, onChange }) => {
  const ref = useRef<HTMLDivElement>(null); // 创建一个 ref 来引用 Popover 组件

  const [isOpen, setIsOpen] = useState(false); // 状态：控制 Popover 是否打开
  const [searchParams, setSearchParams] = useState(""); // 搜索参数状态
  const [formData, setFormData] = useState({ search: "" }); // 表单数据状态

  // 使用 SWR 钩子获取 Unsplash 图片，依赖于 searchParams 变量
  const { data: images } = useSWR(`UNSPLASH_IMAGES_${searchParams}`, () =>
    fileService.getUnsplashImages(1, searchParams)
  );

  // 使用自定义钩子监听点击组件外部事件并关闭 Popover
  useOutsideClickDetector(ref, () => {
    setIsOpen(false);
  });

  // 当 value 或 images 更新时，自动将第一张图片的 URL 设置为当前值（如果没有设置 value）
  useEffect(() => {
    if (!images || value !== null) return;
    onChange(images[0].urls.regular);
  }, [value, onChange, images]);


  return (
    <Popover className="relative z-[2]" ref={ref}>
      <Popover.Button className="rounded-md border border-gray-500 bg-white px-2 py-1 text-xs text-gray-700" onClick={() => setIsOpen((prev) => !prev)}>
        {label} {/* 显示传入的标签 */}
      </Popover.Button>
      <Transition show={isOpen} enter="transition ease-out duration-100" enterFrom="transform opacity-0 scale-95" enterTo="transform opacity-100 scale-100"
        leave="transition ease-in duration-75" leaveFrom="transform opacity-100 scale-100" leaveTo="transform opacity-0 scale-95">
        <Popover.Panel className="absolute right-0 z-10 mt-2 rounded-md bg-white shadow-lg">
          <div className="h-96 w-80 overflow-auto rounded border bg-white p-5 shadow-2xl sm:max-w-2xl md:w-96 lg:w-[40rem]">
            <Tab.Group>
              <Tab.List as="span" className="inline-block rounded bg-gray-200 p-1">
                {tabOptions.map((tab) => ( // 渲染选项卡标题
                  <Tab key={tab.key} className={({ selected }) =>
                    `rounded py-1 px-4 text-center text-sm outline-none transition-colors ${
                      selected ? "bg-theme text-white" : "text-black"
                    }`}>
                    {tab.title}
                  </Tab>
                ))}
              </Tab.List>
              <Tab.Panels className="h-full w-full flex-1 overflow-y-auto overflow-x-hidden"> {/* 定义每个选项卡对应的面板内容 */}
                {/* Unsplash 图片搜索面板 */}
                <Tab.Panel className="h-full w-full space-y-4">
                  {/* 搜索表单 */}
                  <form onSubmit={(e) => {
                      e.preventDefault();
                      setSearchParams(formData.search); // 设置搜索参数并触发图片获取
                    }} className="flex gap-x-2 pt-7">
                    <Input name="search" className="text-sm" id="search" value={formData.search} onChange={(e) => setFormData({ ...formData, search: e.target.value })}
                      placeholder="Search for images"/>
                    <PrimaryButton type="submit" className="bg-indigo-600" size="sm">Search</PrimaryButton> {/* 搜索按钮 */}
                  </form>
                  {/* 根据是否有图片数据来渲染内容 */}
                  {images ? (
                    <div className="grid grid-cols-4 gap-4">
                      {images.map((image) => ( // 渲染图片列表
                        <div key={image.id} className="relative col-span-2 aspect-video md:col-span-1">
                          <Image src={image.urls.small} alt={image.alt_description} layout="fill" objectFit="cover"
                            className="cursor-pointer rounded" onClick={() => {
                              setIsOpen(false); // 点击图片后关闭 Popover 并设置选择的图片 URL
                              onChange(image.urls.regular);
                            }}/>
                        </div>
                      ))}
                    </div>
                  ) : (
                    <div className="flex justify-center pt-20"><Spinner /></div> // 数据加载中显示加载动画 Spinner
                  )}
                </Tab.Panel>
                {/* “上传”选项卡的面板内容，“暂未实现”的提示文本 */}
                <Tab.Panel className="flex h-full w-full flex-col items-center justify-center"><p>Coming Soon...</p></Tab.Panel>
              </Tab.Panels>
            </Tab.Group>
          </div>
        </Popover.Panel>
      </Transition>
    </Popover>
  );
};
