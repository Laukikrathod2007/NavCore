import React from "react";
import { useCountUp } from "../../hooks/useCountUp";

interface AnimatedNumberProps {
  target: number;
  prefix?: string;
  suffix?: string;
  duration?: number;
  decimals?: number;
  style?: React.CSSProperties;
  className?: string;
}

export const AnimatedNumber: React.FC<AnimatedNumberProps> = ({
  target,
  prefix = "",
  suffix = "",
  duration = 1400,
  decimals = 0,
  style,
  className = "",
}) => {
  const { count, ref } = useCountUp(target, duration, decimals);

  return (
    <span ref={ref} style={style} className={className}>
      {prefix}
      {count.toLocaleString()}
      {suffix}
    </span>
  );
};

