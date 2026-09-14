interface StepIndicatorProps {
  steps: string[];
  currentStep: number;
}

export default function StepIndicator({ steps, currentStep }: StepIndicatorProps) {
  return (
    <div className="flex items-start mt-5 overflow-x-auto pb-1 gap-0">
      {steps.map((label, index) => {
        const isDone = index < currentStep;
        const isActive = index === currentStep;

        return (
          <div key={label} className="flex items-start">
            {/* Circle + label */}
            <div className="flex flex-col items-center">
              <div
                className={`
                  w-7 h-7 rounded-full flex items-center justify-center text-xs font-bold
                  border-2 transition-all duration-300 flex-shrink-0
                  ${isDone
                    ? 'bg-skynest-blue border-skynest-blue text-white'
                    : isActive
                    ? 'bg-white border-skynest-blue text-skynest-navy scale-110 shadow-md shadow-skynest-blue/30'
                    : 'bg-transparent border-gray-600 text-gray-500'
                  }
                `}
              >
                {isDone ? '✓' : index + 1}
              </div>
              <span
                className={`
                  text-[9px] mt-1.5 whitespace-nowrap tracking-wide font-semibold
                  ${isActive ? 'text-skynest-blue-light' : isDone ? 'text-skynest-blue/60' : 'text-gray-600'}
                `}
              >
                {label}
              </span>
            </div>

            {/* Connector line */}
            {index < steps.length - 1 && (
              <div
                className={`
                  h-[2px] w-10 sm:w-14 lg:w-20 mt-3.5 mx-1 flex-shrink-0 transition-all duration-500
                  ${isDone ? 'bg-skynest-blue' : 'bg-gray-700'}
                `}
              />
            )}
          </div>
        );
      })}
    </div>
  );
}
