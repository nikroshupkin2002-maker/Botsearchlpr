import { useState, useMemo, useEffect } from "react";
import { motion } from "motion/react";
import { Info, Check, Calculator as CalcIcon, Plus, Settings2, ArrowRight } from "lucide-react";

// Format numbers nicely with spaces
const formatMoney = (val: number) => {
  return new Intl.NumberFormat("ru-RU", { maximumFractionDigits: 0 }).format(Math.round(val));
};

export function Calculator() {
  const [params, setParams] = useState({
    loc: 1,
    chd: 100,
    avg: 5000,
    marg: 70,
    aggr: 30,
    discount: 0,
  });

  const [products, setProducts] = useState({
    p1: false, // Без кассира
    p2: false, // Без официанта
    p3: false, // SR Delivery
    p4: false, // Приложение
    p5: false, // Лояльность
    p6: false, // AppClip
    p7: false, // Автоподтягивание счета
    p8: false, // Киоск
  });

  const [appPrice, setAppPrice] = useState(420000);
  const [appLoc, setAppLoc] = useState(5);
  const [kioskCount, setKioskCount] = useState(1);

  // Update handlers
  const handleParamChange = (field: keyof typeof params, value: number) => {
    setParams(prev => ({ ...prev, [field]: value }));
  };
  
  const toggleProduct = (key: keyof typeof products) => {
    setProducts(prev => ({ ...prev, [key]: !prev[key] }));
  };

  // Calculations
  const results = useMemo(() => {
    const loc = params.loc || 0;
    const chd = params.chd || 0;
    const avg = params.avg || 0;
    const marg = (params.marg || 0) / 100;
    const aggr = (params.aggr || 0) / 100;

    const days = 30;
    const delivery_share = 0.3;
    const impact = 0.4;

    const total_checks = chd * days * loc;
    const base_revenue = total_checks * avg;
    const now_profit = (base_revenue * marg) - (base_revenue * delivery_share * aggr);

    let cost = 0;
    if (products.p1) cost += 84000 * loc;
    if (products.p2) cost += 120000 * loc;
    if (products.p3) cost += 60000 * loc;
    if (products.p4) cost += appPrice || 0;
    if (products.p5) cost += 60000;
    if (products.p6) cost += 35000 * loc;
    if (products.p7) cost += 60000 * loc;
    if (products.p8) cost += 60000 * (kioskCount || 0);

    const has_boost = products.p1 || products.p2 || products.p3 || products.p4 || products.p8;
    const has_speed = products.p2;
    const has_loyalty = products.p5;
    const has_return = products.p1 || products.p2 || products.p3 || products.p4 || products.p5 || products.p7 || products.p8;

    const n_avg = has_boost ? (avg * (1 - impact)) + (avg * 1.16 * impact) : avg;
    const n_ch = has_speed ? (total_checks * (1 - impact)) + (total_checks * 1.25 * impact) : total_checks;
    
    const ret_rev = has_return ? (n_ch * 0.2 * n_avg) : 0;
    const loy_rev = has_loyalty ? (n_ch * 0.2 * n_avg * 0.3) : 0;

    const smart_rev = (n_ch * n_avg) + ret_rev + loy_rev;

    const discount = params.discount || 0;
    const final_cost = cost * (1 - discount / 100);

    let smart_profit = (smart_rev * marg) - final_cost;
    if (!products.p3) {
      smart_profit -= (smart_rev * delivery_share * aggr);
    }

    const diff = smart_profit - now_profit;

    return { now_profit, smart_profit, diff, cost: final_cost };
  }, [params, products, appPrice, kioskCount]);

  const InputField = ({ label, value, field, min=0, max=1000000, suffix="" }: any) => (
    <div className="flex flex-col gap-1.5 w-full">
      <label className="text-sm font-semibold text-gray-600">{label}</label>
      <div className="relative flex items-center">
        <input
          type="number"
          min={min}
          max={max}
          value={value}
          onChange={(e) => handleParamChange(field, parseFloat(e.target.value) || 0)}
          className="w-full h-12 px-4 rounded-xl border border-gray-200 bg-gray-50 text-gray-900 font-medium focus:outline-none focus:ring-2 focus:ring-[#1FCC59]/30 focus:border-[#1FCC59] focus:bg-white transition-all appearance-none"
        />
        {suffix && <span className="absolute right-4 text-gray-400 font-medium">{suffix}</span>}
      </div>
    </div>
  );

  const ProductCard = ({ id, label, priceLabel, isChecked, onToggle, extraInputs = null }: any) => (
    <div
      className={`relative flex flex-col p-4 sm:p-5 rounded-2xl border-2 transition-all cursor-pointer select-none
        ${isChecked ? 'border-[#1FCC59] bg-[#1FCC59]/5 shadow-sm' : 'border-transparent bg-white shadow-sm hover:shadow-md'}
      `}
      onClick={onToggle}
    >
      <div className="flex justify-between items-start mb-1 gap-2">
        <h4 className={`font-bold text-[15px] leading-tight ${isChecked ? 'text-gray-900' : 'text-gray-700'}`}>
          {label}
        </h4>
        <div className={`w-5 h-5 flex-shrink-0 rounded-md flex items-center justify-center transition-colors ${isChecked ? 'bg-[#1FCC59] text-white' : 'bg-gray-100 border border-gray-300'}`}>
          {isChecked && <Check size={14} strokeWidth={3} />}
        </div>
      </div>
      <p className="text-xs font-semibold text-gray-400 uppercase tracking-wide">
        {priceLabel}
      </p>

      {/* Render extra inputs (like for App or Kiosk) when checked, but stop propagation so clicking input doesn't toggle card */}
      {isChecked && extraInputs && (
        <div className="mt-4 border-t border-[#1FCC59]/20 pt-4" onClick={(e) => e.stopPropagation()}>
          {extraInputs}
        </div>
      )}
    </div>
  );

  return (
    <div className="container mx-auto px-4 sm:px-8 py-8 md:py-12 max-w-6xl pb-24 lg:pb-12">
      <div className="flex flex-col lg:flex-row gap-8 lg:gap-12 relative">
        
        {/* Left Column: Form Controls */}
        <div className="w-full lg:w-[65%] flex flex-col gap-8 pb-12">
          
          <div className="mb-2">
            <h1 className="text-3xl md:text-4xl font-bold text-gray-900 tracking-tight flex items-center gap-3">
              <CalcIcon size={32} className="text-[#1FCC59]" />
              Smart Restaurant Calc
            </h1>
            <div className="inline-flex items-center mt-4 bg-blue-50 text-blue-700 text-sm font-semibold px-4 py-2 rounded-lg border border-blue-100">
              <Info size={16} className="mr-2 opacity-80" />
              Расчет ведется на 40% проникновения продукта
            </div>
          </div>

          <section>
            <h2 className="text-lg font-bold text-gray-900 mb-4 uppercase tracking-wider flex items-center gap-2">
              <Settings2 size={20} className="text-gray-400" />
              1. Основные параметры
            </h2>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4 bg-white p-6 rounded-3xl shadow-sm border border-gray-100">
              <InputField label="Локаций" value={params.loc} field="loc" />
              <InputField label="Чеков/день" value={params.chd} field="chd" />
              <InputField label="Ср. чек" value={params.avg} field="avg" suffix="₸" />
              <InputField label="Маржа" value={params.marg} field="marg" suffix="%" max={100} />
            </div>
          </section>

          <section>
            <h2 className="text-lg font-bold text-gray-900 mb-4 uppercase tracking-wider flex items-center gap-2">
              <Plus size={20} className="text-gray-400" />
              2. Дополнительные параметры
            </h2>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4 bg-white p-6 rounded-3xl shadow-sm border border-gray-100">
              <InputField label="Комиссия агр." value={params.aggr} field="aggr" suffix="%" max={100} />
              <InputField label="Скидка на услуги" value={params.discount} field="discount" suffix="%" max={100} />
            </div>
          </section>

          <section>
            <h2 className="text-lg font-bold text-gray-900 mb-4 uppercase tracking-wider flex items-center gap-2">
              <Check size={20} className="text-gray-400" />
              3. Продукты
            </h2>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <ProductCard 
                id="p1" 
                label="Без кассира" 
                priceLabel="84 000 ₸ / лок" 
                isChecked={products.p1} 
                onToggle={() => toggleProduct('p1')} 
              />
              <ProductCard 
                id="p2" 
                label="Без официанта" 
                priceLabel="120 000 ₸ / лок" 
                isChecked={products.p2} 
                onToggle={() => toggleProduct('p2')} 
              />
              <ProductCard 
                id="p3" 
                label="SR Delivery" 
                priceLabel="60 000 ₸ / лок" 
                isChecked={products.p3} 
                onToggle={() => toggleProduct('p3')} 
              />
              <ProductCard 
                id="p4" 
                label="Приложение" 
                priceLabel="Настраиваемая цена" 
                isChecked={products.p4} 
                onToggle={() => toggleProduct('p4')} 
                extraInputs={
                  <div className="flex flex-col gap-3">
                    <div className="flex flex-col gap-1 w-full">
                      <label className="text-xs font-semibold text-gray-600">Цена приложения (₸)</label>
                      <input type="number" value={appPrice} onChange={e => setAppPrice(parseFloat(e.target.value)||0)} className="w-full h-10 px-3 rounded-lg border border-[#1FCC59]/30 bg-white text-sm" />
                    </div>
                    <div className="flex flex-col gap-1 w-full">
                      <label className="text-xs font-semibold text-gray-600">Локаций приложения</label>
                      <input type="number" value={appLoc} onChange={e => setAppLoc(parseFloat(e.target.value)||0)} className="w-full h-10 px-3 rounded-lg border border-[#1FCC59]/30 bg-white text-sm" />
                    </div>
                  </div>
                }
              />
              <ProductCard 
                id="p5" 
                label="Лояльность" 
                priceLabel="60 000 ₸" 
                isChecked={products.p5} 
                onToggle={() => toggleProduct('p5')} 
              />
              <ProductCard 
                id="p6" 
                label="AppClip" 
                priceLabel="35 000 ₸ / лок" 
                isChecked={products.p6} 
                onToggle={() => toggleProduct('p6')} 
              />
              <ProductCard 
                id="p7" 
                label="Автоподтягивание счета" 
                priceLabel="60 000 ₸ / лок" 
                isChecked={products.p7} 
                onToggle={() => toggleProduct('p7')} 
              />
              <ProductCard 
                id="p8" 
                label="Киоск" 
                priceLabel="60 000 ₸ / ед" 
                isChecked={products.p8} 
                onToggle={() => toggleProduct('p8')} 
                extraInputs={
                  <div className="flex flex-col gap-1 w-full mt-1">
                    <label className="text-xs font-semibold text-gray-600">Кол-во киосков</label>
                    <div className="flex items-center gap-2">
                      <button onClick={(e) => { e.stopPropagation(); setKioskCount(Math.max(1, kioskCount - 1)); }} className="w-8 h-8 rounded-lg bg-[#1FCC59]/10 text-[#1FCC59] flex items-center justify-center hover:bg-[#1FCC59]/20">-</button>
                      <input type="number" min={1} value={kioskCount} onChange={e => setKioskCount(parseInt(e.target.value)||1)} className="w-full text-center h-10 px-3 rounded-lg border border-[#1FCC59]/30 bg-white text-sm font-bold" />
                      <button onClick={(e) => { e.stopPropagation(); setKioskCount(kioskCount + 1); }} className="w-8 h-8 rounded-lg bg-[#1FCC59]/10 text-[#1FCC59] flex items-center justify-center hover:bg-[#1FCC59]/20">+</button>
                    </div>
                  </div>
                }
              />
            </div>
          </section>

        </div>

        {/* Right Column: Results sticky panel */}
        <div className="w-full lg:w-[35%] relative">
          <motion.div 
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.6 }}
            className="sticky top-24 flex flex-col gap-6"
          >
            {/* The Before / After Cards */}
            <div className="bg-white rounded-[32px] p-6 sm:p-8 shadow-xl shadow-gray-200/50 border border-gray-100 flex flex-col">
              <h3 className="text-xl font-bold text-gray-900 mb-6 text-center">Итоговый расчет за 30 дней</h3>

              {/* Now Card */}
              <div className="bg-gray-50 rounded-2xl p-5 mb-4 border border-gray-100 flex flex-col items-center justify-center text-center">
                <span className="text-xs font-bold text-gray-400 uppercase tracking-widest mb-1">Прибыль сейчас</span>
                <span className="text-3xl font-extrabold text-gray-800 tracking-tight">
                  {formatMoney(results.now_profit)} <span className="text-xl text-gray-500">₸</span>
                </span>
              </div>

              {/* Arrow Down Indicator */}
              <div className="flex justify-center -my-2 relative z-10 hidden sm:flex">
                <div className="w-8 h-8 bg-white border border-gray-100 rounded-full flex items-center justify-center shadow-sm">
                  <ArrowRight size={16} className="text-gray-300 transform rotate-90" strokeWidth={3} />
                </div>
              </div>

              {/* Smart Restaurant Card */}
              <div className="bg-gradient-to-br from-[#1FCC59] to-[#0CB055] rounded-2xl p-6 text-white flex flex-col items-center justify-center text-center shadow-lg shadow-[#1FCC59]/20">
                <span className="text-xs font-bold text-white/80 uppercase tracking-widest mb-1">С Smart Restaurant</span>
                <span className="text-3xl sm:text-4xl font-extrabold tracking-tight">
                  {formatMoney(results.smart_profit)} <span className="text-xl sm:text-2xl text-white/80">₸</span>
                </span>
                
                {results.cost > 0 && (
                   <span className="mt-3 text-xs font-medium text-white/80 bg-white/10 px-3 py-1 rounded-full">
                     Затраты на продукты: -{formatMoney(results.cost)} ₸
                   </span>
                )}
              </div>

              {/* Total Benefit Card */}
              <motion.div 
                key={results.diff}
                initial={{ scale: 0.95 }}
                animate={{ scale: 1 }}
                className={`mt-6 rounded-2xl p-5 border-2 flex items-center justify-center ${results.diff >= 0 ? 'bg-[#1FCC59]/10 border-[#1FCC59]/30 text-[#0CB055]' : 'bg-red-50 border-red-200 text-red-600'}`}
              >
                <div className="text-center">
                  <span className="text-sm font-bold uppercase tracking-wider block mb-1">
                    Выгода от внедрения
                  </span>
                  <span className="text-2xl font-black">
                    {results.diff > 0 ? '+' : ''}{formatMoney(results.diff)} ₸
                  </span>
                </div>
              </motion.div>
            </div>
          </motion.div>
        </div>
      </div>

      {/* Floating Mobile Sticky Footer for quick results */}
      <div className="lg:hidden fixed bottom-0 left-0 right-0 bg-white border-t border-gray-200 p-4 shadow-[0_-4px_20px_rgba(0,0,0,0.05)] z-40 flex items-center justify-between">
        <div className="flex flex-col">
          <span className="text-[10px] font-bold text-gray-500 uppercase tracking-widest">Выгода</span>
          <span className={`text-lg font-black ${results.diff >= 0 ? 'text-[#0CB055]' : 'text-red-600'}`}>
            {results.diff > 0 ? '+' : ''}{formatMoney(results.diff)} ₸
          </span>
        </div>
        <div className="flex flex-col items-end">
          <span className="text-[10px] font-bold text-gray-500 uppercase tracking-widest">Прибыль (Smart)</span>
          <span className="text-lg font-black text-gray-900">
            {formatMoney(results.smart_profit)} ₸
          </span>
        </div>
      </div>

    </div>
  );
}
