import type { SVGProps } from "react";

type KhukraMarkProps = SVGProps<SVGSVGElement> & {
  accentColor?: string;
};

export function KhukraMark({
  accentColor = "currentColor",
  className,
  ...props
}: KhukraMarkProps) {
  return (
    <svg
      viewBox="0 0 64 64"
      aria-hidden="true"
      className={className}
      fill="none"
      {...props}
    >
      <path
        d="M12 42C24 22 40 10 56 11C47 17 39 26 34 37C29 47 22 50 14 46"
        stroke={accentColor}
        strokeWidth="6"
        strokeLinecap="round"
        strokeLinejoin="round"
      />
      <path
        d="M14 42L8 51M18 45L12 54"
        stroke="currentColor"
        strokeWidth="4"
        strokeLinecap="round"
      />
      <path
        d="M30 31C33 30 36 28 39 25"
        stroke="currentColor"
        strokeWidth="2.5"
        strokeLinecap="round"
        opacity="0.55"
      />
      <circle cx="43" cy="22" r="2.5" fill={accentColor} />
    </svg>
  );
}

export function KhukraLogo({
  className,
  accentColor = "currentColor",
  subtitle,
}: {
  className?: string;
  accentColor?: string;
  subtitle?: string;
}) {
  return (
    <div className={`flex items-center gap-3 ${className ?? ""}`}>
      <div className="flex h-11 w-11 shrink-0 items-center justify-center rounded-2xl border border-white/10 bg-white/[0.04]">
        <KhukraMark className="h-7 w-7 text-white" accentColor={accentColor} />
      </div>
      <div>
        <p className="text-xs font-medium uppercase tracking-[0.28em] text-zinc-500">
          Khukra
        </p>
        {subtitle && <p className="mt-1 text-xs text-zinc-600">{subtitle}</p>}
      </div>
    </div>
  );
}
