import { useState } from "react";

// components
import { DeleteCycleModal, SingleCycleCard } from "components/cycles";
import { EmptyState, Loader } from "components/ui";
// image
import emptyCycle from "public/empty-state/empty-cycle.svg";
// icon
import { XMarkIcon } from "@heroicons/react/24/outline";
// types
import { ICycle, SelectCycleType } from "types";

type TCycleStatsViewProps = {
  cycles: ICycle[] | undefined;
  setCreateUpdateCycleModal: React.Dispatch<React.SetStateAction<boolean>>;
  setSelectedCycle: React.Dispatch<React.SetStateAction<SelectCycleType>>;
  type: "current" | "upcoming" | "draft";
};

export const CyclesList: React.FC<TCycleStatsViewProps> = ({
  cycles,
  setCreateUpdateCycleModal,
  setSelectedCycle,
  type,
}) => {
  const [cycleDeleteModal, setCycleDeleteModal] = useState(false);
  const [selectedCycleForDelete, setSelectedCycleForDelete] = useState<SelectCycleType>();
  const [showNoCurrentCycleMessage, setShowNoCurrentCycleMessage] = useState(true);

  const handleDeleteCycle = (cycle: ICycle) => {
    setSelectedCycleForDelete({ ...cycle, actionType: "delete" });
    setCycleDeleteModal(true);
  };

  const handleEditCycle = (cycle: ICycle) => {
    setSelectedCycle({ ...cycle, actionType: "edit" });
    setCreateUpdateCycleModal(true);
  };

  return (
    <>
      <DeleteCycleModal
        isOpen={
          cycleDeleteModal &&
          !!selectedCycleForDelete &&
          selectedCycleForDelete.actionType === "delete"
        }
        setIsOpen={setCycleDeleteModal}
        data={selectedCycleForDelete}
      />
      {cycles ? (
        cycles.length > 0 ? (
          <div className="grid grid-cols-1 gap-9 md:grid-cols-2 lg:grid-cols-3">
            {cycles.map((cycle) => (
              <SingleCycleCard
                key={cycle.id}
                cycle={cycle}
                handleDeleteCycle={() => handleDeleteCycle(cycle)}
                handleEditCycle={() => handleEditCycle(cycle)}
              />
            ))}
          </div>
        ) : type === "current" ? (
          showNoCurrentCycleMessage && (
            <div className="flex items-center justify-between bg-white w-full px-6 py-4 rounded-[10px]">
              <h3 className="text-base font-medium text-black "> No current cycle is present.</h3>
              <button onClick={() => setShowNoCurrentCycleMessage(false)}>
                <XMarkIcon className="h-4 w-4" />
              </button>
            </div>
          )
        ) : (
          <EmptyState
            type="cycle"
            title="创建一个新的Cycle"
            description="通过将项目限制在固定的时间内，使用 Cycles 来更有效地进行冲刺。"
            imgURL={emptyCycle}
          />
        )
      ) : (
        <Loader className="grid grid-cols-1 gap-9 md:grid-cols-2 lg:grid-cols-3">
          <Loader.Item height="200px" />
        </Loader>
      )}
    </>
  );
};
