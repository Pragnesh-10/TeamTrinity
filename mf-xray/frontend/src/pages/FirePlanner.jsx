import React, { useState, useEffect } from 'react';
import { getFirePlan } from '../lib/api';

export default function FirePlanner({ initialInput = {}, title = 'FIRE Planner' }) {
  const getDefaultForm = () => ({
    age: 34,
    monthly_income: 200000,
    monthly_expenses: 80000,
    target_retirement_age: 50,
    existing_investments: 0,
    expected_return: null,
    inflation_rate: null,
    equity_allocation_start: 0.8,
    equity_allocation_end: 0.5,
    sip_equity: 0,
    sip_debt: 0,
    current_life_cover: 0,
    recommended_income_multiple: 15,
    ...initialInput,
  });
  const [form, setForm] = useState(getDefaultForm);

  const [plan, setPlan] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const updateField = (field, value) => {
    setForm((prev) => ({
      ...prev,
      [field]: value,
    }));
  };

  useEffect(() => {
    setForm((prev) => ({
      ...prev,
      ...initialInput,
    }));
  }, [initialInput]);

  useEffect(() => {
    const hasRequiredInputs =
      Number(form.age) >= 18 &&
      Number(form.target_retirement_age) > Number(form.age) &&
      Number(form.monthly_income) > 0 &&
      Number(form.monthly_expenses) > 0;

    if (!hasRequiredInputs) {
      setPlan(null);
      setLoading(false);
      setError(null);
      return undefined;
    }

    let cancelled = false;
    const handler = setTimeout(async () => {
      try {
        setLoading(true);
        setError(null);
        const result = await getFirePlan(form);
        if (!cancelled) {
          setPlan(result);
        }
      } catch (e) {
        if (!cancelled) {
          setError(e.message || 'Failed to compute FIRE plan');
        }
      } finally {
        if (!cancelled) {
          setLoading(false);
        }
      }
    }, 500);

    return () => {
      cancelled = true;
      clearTimeout(handler);
    };
  }, [form]);

  const core = plan?.core_result;
  const insurance = plan?.insurance_gap;

  return (
    <div className="w-full">
      <div className="w-full grid gap-8 md:grid-cols-[minmax(0,1.3fr)_minmax(0,1fr)]">
        <div>
          <h2 className="text-2xl font-bold mb-3 tracking-tight">{title}</h2>
          <p className="text-gray-400 mb-6">
            Structured inputs for a dynamic retirement plan. Change any field to
            instantly recompute your path.
          </p>

          <div className="space-y-4">
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm text-gray-400 mb-1">Current Age</label>
                <input
                  type="number"
                  className="w-full bg-surface border border-border rounded-lg p-2"
                  value={form.age}
                  onChange={(e) => updateField('age', Number(e.target.value))}
                />
              </div>
              <div>
                <label className="block text-sm text-gray-400 mb-1">Target Retirement Age</label>
                <input
                  type="number"
                  className="w-full bg-surface border border-border rounded-lg p-2"
                  value={form.target_retirement_age}
                  onChange={(e) =>
                    updateField('target_retirement_age', Number(e.target.value))
                  }
                />
              </div>
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm text-gray-400 mb-1">Monthly Income (₹)</label>
                <input
                  type="number"
                  className="w-full bg-surface border border-border rounded-lg p-2"
                  value={form.monthly_income}
                  onChange={(e) =>
                    updateField('monthly_income', Number(e.target.value))
                  }
                />
              </div>
              <div>
                <label className="block text-sm text-gray-400 mb-1">Monthly Expenses (₹)</label>
                <input
                  type="number"
                  className="w-full bg-surface border border-border rounded-lg p-2"
                  value={form.monthly_expenses}
                  onChange={(e) =>
                    updateField('monthly_expenses', Number(e.target.value))
                  }
                />
              </div>
            </div>

            <div>
              <label className="block text-sm text-gray-400 mb-1">
                Existing Investments (₹, total corpus)
              </label>
              <input
                type="number"
                className="w-full bg-surface border border-border rounded-lg p-2"
                value={form.existing_investments}
                onChange={(e) =>
                  updateField('existing_investments', Number(e.target.value))
                }
              />
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm text-gray-400 mb-1">
                  Equity Allocation Start (%)
                </label>
                <input
                  type="number"
                  className="w-full bg-surface border border-border rounded-lg p-2"
                  min={0}
                  max={100}
                  value={form.equity_allocation_start * 100}
                  onChange={(e) =>
                    updateField('equity_allocation_start', Number(e.target.value) / 100)
                  }
                />
              </div>
              <div>
                <label className="block text-sm text-gray-400 mb-1">
                  Equity Allocation at Retirement (%)
                </label>
                <input
                  type="number"
                  className="w-full bg-surface border border-border rounded-lg p-2"
                  min={0}
                  max={100}
                  value={form.equity_allocation_end * 100}
                  onChange={(e) =>
                    updateField('equity_allocation_end', Number(e.target.value) / 100)
                  }
                />
              </div>
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm text-gray-400 mb-1">
                  Equity SIP (₹/month)
                </label>
                <input
                  type="number"
                  className="w-full bg-surface border border-border rounded-lg p-2"
                  value={form.sip_equity}
                  onChange={(e) =>
                    updateField('sip_equity', Number(e.target.value))
                  }
                />
              </div>
              <div>
                <label className="block text-sm text-gray-400 mb-1">
                  Debt SIP (₹/month)
                </label>
                <input
                  type="number"
                  className="w-full bg-surface border border-border rounded-lg p-2"
                  value={form.sip_debt}
                  onChange={(e) => updateField('sip_debt', Number(e.target.value))}
                />
              </div>
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm text-gray-400 mb-1">
                  Current Life Cover (₹)
                </label>
                <input
                  type="number"
                  className="w-full bg-surface border border-border rounded-lg p-2"
                  value={form.current_life_cover}
                  onChange={(e) =>
                    updateField('current_life_cover', Number(e.target.value))
                  }
                />
              </div>
              <div>
                <label className="block text-sm text-gray-400 mb-1">
                  Recommended Cover Multiple (x annual expenses)
                </label>
                <input
                  type="number"
                  className="w-full bg-surface border border-border rounded-lg p-2"
                  value={form.recommended_income_multiple}
                  onChange={(e) =>
                    updateField(
                      'recommended_income_multiple',
                      Number(e.target.value)
                    )
                  }
                />
              </div>
            </div>
          </div>
        </div>

        <div className="bg-surface border border-border rounded-2xl p-5 flex flex-col gap-4">
          {loading && <p className="text-teal text-sm">Recomputing plan…</p>}
          {error && <p className="text-red-400 text-sm">{error}</p>}

          {core ? (
            <>
              <div>
                <h2 className="font-semibold mb-1">Core FIRE Metrics</h2>
                <p className="text-sm text-gray-400">
                  Target corpus:{' '}
                  <span className="text-white">
                    ₹{core.target_corpus.toLocaleString('en-IN')}
                  </span>
                </p>
                <p className="text-sm text-gray-400">
                  Required SIP:{' '}
                  <span className="text-white">
                    ₹{core.monthly_sip_needed.toLocaleString('en-IN')}/month
                  </span>
                </p>
                <p className="text-sm text-gray-400">
                  Years to FIRE:{' '}
                  <span className="text-white">{core.years_to_fire}</span>
                </p>
                <p className="text-sm text-gray-400">
                  Projected corpus at retirement:{' '}
                  <span className="text-white">
                    ₹{core.projected_corpus_at_retirement.toLocaleString('en-IN')}
                  </span>
                </p>
              </div>

              {plan?.estimated_retirement_age && (
                <div>
                  <h2 className="font-semibold mb-1">Estimated Retirement Age</h2>
                  <p className="text-sm text-gray-400">
                    Estimated sustainable retirement age:{' '}
                    <span className="text-white">
                      {plan.estimated_retirement_age.toFixed(1)} years
                    </span>
                  </p>
                </div>
              )}

              {insurance && (
                <div>
                  <h2 className="font-semibold mb-1">Insurance Gap</h2>
                  <p className="text-sm text-gray-400">
                    Required cover:{' '}
                    <span className="text-white">
                      ₹{insurance.required_cover.toLocaleString('en-IN')}
                    </span>
                  </p>
                  <p className="text-sm text-gray-400">
                    Current cover:{' '}
                    <span className="text-white">
                      ₹{insurance.current_cover.toLocaleString('en-IN')}
                    </span>
                  </p>
                  <p className="text-sm text-gray-400">
                    Gap:{' '}
                    <span className="text-white">
                      ₹{insurance.gap.toLocaleString('en-IN')}
                    </span>
                  </p>
                </div>
              )}

              {plan?.warnings?.length ? (
                <div>
                  <h2 className="font-semibold mb-1">Warnings</h2>
                  <ul className="list-disc list-inside text-sm text-amber-300">
                    {plan.warnings.map((w, idx) => (
                      <li key={idx}>{w}</li>
                    ))}
                  </ul>
                </div>
              ) : null}
            </>
          ) : (
            <p className="text-gray-400 text-sm">
              Enter valid age, retirement age, income, and expenses to generate your live FIRE plan.
            </p>
          )}
        </div>
      </div>
    </div>
  );
}

