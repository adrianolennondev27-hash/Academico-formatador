interface LogoProps {
  size?: number;
  showText?: boolean;
}

export default function Logo({ size = 48, showText = true }: LogoProps) {
  return (
    <div className="flex items-center gap-3">
      <div
        className="relative flex items-center justify-center rounded-full shadow-lg"
        style={{
          width: size,
          height: size,
          background:
            "linear-gradient(135deg, #1e3a8a 0%, #3b82f6 60%, #dc2626 100%)",
        }}
      >
        <span
          className="font-black text-white italic"
          style={{ fontSize: size * 0.55, lineHeight: 1 }}
        >
          F
        </span>
        <svg
          className="absolute -right-1 -top-1 animate-wing"
          width={size * 0.5}
          height={size * 0.5}
          viewBox="0 0 24 24"
          fill="none"
        >
          <path
            d="M2 12 C6 8, 12 6, 22 4 C18 8, 14 12, 2 12 Z"
            fill="#dc2626"
          />
        </svg>
      </div>
      {showText && (
        <div className="flex flex-col leading-none">
          <span className="text-2xl font-black text-slate-900 tracking-tight">
            FVA
          </span>
          <span className="text-[10px] text-slate-500 font-medium tracking-wider uppercase">
            Formatador e Validador Acadêmico
          </span>
        </div>
      )}
    </div>
  );
}