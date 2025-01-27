import React, { useEffect, useState } from "react";
// headless ui
import { Dialog, Transition } from "@headlessui/react";
// icons
import { XMarkIcon } from "@heroicons/react/20/solid";
import { MagnifyingGlassIcon } from "@heroicons/react/24/outline";
import { MacCommandIcon } from "components/icons";
// ui
import { Input } from "components/ui";

type Props = {
  isOpen: boolean;
  setIsOpen: React.Dispatch<React.SetStateAction<boolean>>;
};

const shortcuts = [
  {
    title: "导航栏",
    shortcuts: [
      { keys: "Ctrl,K", description: "打开导航" },
      { keys: "↑", description: "向上移动" },
      { keys: "↓", description: "向下移动" },
      { keys: "←", description: "向左移动" },
      { keys: "→", description: "向右移动" },
      { keys: "Enter", description: "选择" },
      { keys: "Esc", description: "关闭" },
    ],
  },
  {
    title: "通用",
    shortcuts: [
      { keys: "P", description: "创建一个新的项目" },
      { keys: "C", description: "创建一个新的issue" },
      { keys: "Q", description: "创建一个新的cycle" },
      // { keys: "M", description: "To create module" },
      // { keys: "V", description: "To create view" },
      { keys: "D", description: "创建一个新的page" },
      // { keys: "Delete", description: "To bulk delete issues" },
      { keys: "H", description: "打开快捷键指南" },
      // {
      //   keys: "Ctrl,Alt,C",
      //   description: "To copy issue url when on issue detail page",
      // },
    ],
  },
];

const allShortcuts = shortcuts.map((i) => i.shortcuts).flat(1);

export const ShortcutsModal: React.FC<Props> = ({ isOpen, setIsOpen }) => {
  const [query, setQuery] = useState("");
  const filteredShortcuts = allShortcuts.filter((shortcut) =>
    shortcut.description.toLowerCase().includes(query.trim().toLowerCase()) || query === ""
      ? true
      : false
  );

  useEffect(() => {
    if (!isOpen) setQuery("");
  }, [isOpen]);

  return (
    <Transition.Root show={isOpen} as={React.Fragment}>
      <Dialog as="div" className="relative z-20" onClose={setIsOpen}>
        <Transition.Child
          as={React.Fragment}
          enter="ease-out duration-300"
          enterFrom="opacity-0"
          enterTo="opacity-100"
          leave="ease-in duration-200"
          leaveFrom="opacity-100"
          leaveTo="opacity-0"
        >
          <div className="fixed inset-0 bg-gray-500 bg-opacity-75 transition-opacity" />
        </Transition.Child>

        <div className="fixed inset-0 z-20 overflow-y-auto">
          <div className="flex min-h-full items-end justify-center p-4 text-center sm:items-center sm:p-0">
            <Transition.Child
              as={React.Fragment}
              enter="ease-out duration-300"
              enterFrom="opacity-0 translate-y-4 sm:translate-y-0 sm:scale-95"
              enterTo="opacity-100 translate-y-0 sm:scale-100"
              leave="ease-in duration-200"
              leaveFrom="opacity-100 translate-y-0 sm:scale-100"
              leaveTo="opacity-0 translate-y-4 sm:translate-y-0 sm:scale-95"
            >
              <Dialog.Panel className="relative transform overflow-hidden rounded-lg bg-white text-left shadow-xl transition-all sm:my-8 sm:w-full sm:max-w-lg">
                <div className="bg-white p-5">
                  <div className="sm:flex sm:items-start">
                    <div className="flex w-full flex-col gap-y-4 text-center sm:text-left">
                      <Dialog.Title
                        as="h3"
                        className="flex justify-between text-lg font-medium leading-6 text-gray-900"
                      >
                        <span>快捷键指南</span>
                        <span>
                          <button type="button" onClick={() => setIsOpen(false)}>
                            <XMarkIcon
                              className="h-6 w-6 text-gray-400 hover:text-gray-500"
                              aria-hidden="true"
                            />
                          </button>
                        </span>
                      </Dialog.Title>

                      <div className="flex w-full flex-col gap-y-3">
                        {query.trim().length > 0 ? (
                          filteredShortcuts.length > 0 ? (
                            filteredShortcuts.map((shortcut) => (
                              <div key={shortcut.keys} className="flex w-full flex-col">
                                <div className="flex flex-col gap-y-3">
                                  <div className="flex items-center justify-between">
                                    <p className="text-sm text-gray-500">{shortcut.description}</p>
                                    <div className="flex items-center gap-x-2.5">
                                      {shortcut.keys.split(",").map((key, index) => (
                                        <span key={index} className="flex items-center gap-1">
                                          {key === "Ctrl" ? (
                                            <span className="flex h-full items-center rounded-sm border border-gray-200 bg-gray-100 p-2">
                                              <MacCommandIcon />
                                            </span>
                                          ) : (
                                            <kbd className="rounded-sm border border-gray-200 bg-gray-100 px-2 py-1 text-sm font-medium text-gray-800">
                                              {key === "Ctrl" ? <MacCommandIcon /> : key}
                                            </kbd>
                                          )}
                                        </span>
                                      ))}
                                    </div>
                                  </div>
                                </div>
                              </div>
                            ))
                          ) : (
                            <div className="flex flex-col gap-y-3">
                              <p className="text-sm text-gray-500">
                                No shortcuts found for{" "}
                                <span className="font-semibold italic">
                                  {`"`}
                                  {query}
                                  {`"`}
                                </span>
                              </p>
                            </div>
                          )
                        ) : (
                          shortcuts.map(({ title, shortcuts }) => (
                            <div key={title} className="flex w-full flex-col">
                              <p className="mb-4 font-medium">{title}</p>
                              <div className="flex flex-col gap-y-3">
                                {shortcuts.map(({ keys, description }, index) => (
                                  <div key={index} className="flex items-center justify-between">
                                    <p className="text-sm text-gray-500">{description}</p>
                                    <div className="flex items-center gap-x-2.5">
                                      {keys.split(",").map((key, index) => (
                                        <span key={index} className="flex items-center gap-1">
                                          {key === "Ctrl" ? (
                                            <span className="flex h-full items-center rounded-sm border border-gray-200 bg-gray-100 p-2">
                                              <MacCommandIcon />
                                            </span>
                                          ) : (
                                            <kbd className="rounded-sm border border-gray-200 bg-gray-100 px-2 py-1 text-sm font-medium text-gray-800">
                                              {key === "Ctrl" ? <MacCommandIcon /> : key}
                                            </kbd>
                                          )}
                                        </span>
                                      ))}
                                    </div>
                                  </div>
                                ))}
                              </div>
                            </div>
                          ))
                        )}
                      </div>
                    </div>
                  </div>
                </div>
              </Dialog.Panel>
            </Transition.Child>
          </div>
        </div>
      </Dialog>
    </Transition.Root>
  );
};
