
import { useEffect, useState, type FormEvent } from 'react'
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts'

type StrategyMetrics = {
  total_return: number
  sharpe_ratio: number
  annualized_volatility: number
  max_drawdown: number
}

type BacktestResponse = {
  id: number
  status: string
  message?: string
  strategy_metrics?: StrategyMetrics | null
  final_equity?: number | null
  benchmark_final_equity?: number | null
}

type EquityPoint = {
  trading_date: string
  equity: number
  benchmark_equity: number
  position: number
}

function formatPercent(value: number) {
  return `${(value * 100).toFixed(2)}%`
}

function App() {
  const [symbol, setSymbol] = useState('AAPL')
  const [start, setStart] = useState('2024-01-01')
  const [end, setEnd] = useState('2025-01-01')
  const [lookback, setLookback] = useState(20)
  const [initialCapital, setInitialCapital] = useState(10000)

  const [loading, setLoading] = useState(false)
  const [backtest, setBacktest] = useState<BacktestResponse | null>(null)
  const [error, setError] = useState<string | null>(null)

  const [equityData, setEquityData] = useState<EquityPoint[]>([])
  const [equityError, setEquityError] = useState<string | null>(null)

  useEffect(() => {
    if (!backtest) return

    const backtestId = backtest.id

    if (backtest.status === 'COMPLETED' || backtest.status === 'FAILED') {
      return
    }

    let active = true
    let inFlight = false

    const poll = async () => {
      if (inFlight) return
      inFlight = true

      try {
        const response = await fetch(`/api/backtests/${backtestId}`)

        if (!response.ok) {
          throw new Error(`Failed to fetch status: ${response.status}`)
        }

        const data = await response.json()

        if (active) {
          setBacktest((current) =>
            current?.id === backtestId
              ? { ...current, ...data }
              : current
          )
          setError(null)
        }
      } catch (err) {
        if (active) {
          setError(
            err instanceof Error ? err.message : 'Failed to fetch status'
          )
        }
      } finally {
        inFlight = false
      }
    }

    void poll()
    const interval = window.setInterval(() => void poll(), 2000)

    return () => {
      active = false
      window.clearInterval(interval)
    }
  }, [backtest?.id, backtest?.status])


useEffect(() => {
  if (!backtest || backtest.status !== 'COMPLETED') return

  const controller = new AbortController()

  async function fetchEquity() {
    try {
      const response = await fetch(
        `/api/backtests/${backtest!.id}/equity`,
        { signal: controller.signal }
      )

      if (!response.ok) {
        throw new Error(`Failed to fetch equity data: ${response.status}`)
      }

      const data: EquityPoint[] = await response.json()

      if (!controller.signal.aborted) {
        setEquityData(data)
        setEquityError(null)
      }
    } catch (err) {
      if (controller.signal.aborted) return

      setEquityError(
        err instanceof Error ? err.message : 'Failed to load equity data'
      )
    }
  }

  void fetchEquity()

  return () => controller.abort()
}, [backtest?.id, backtest?.status])


  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()

    setLoading(true)
    setError(null)
    setBacktest(null)

    setEquityData([])
    setEquityError(null)

    try {
      const response = await fetch('/api/backtests', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          symbol: symbol.trim().toUpperCase(),
          start,
          end,
          lookback,
          initial_capital: initialCapital,
        }),
      })

      if (!response.ok) {
        throw new Error(`Request failed: ${response.status}`)
      }

      const data: BacktestResponse = await response.json()
      setBacktest(data)
    } catch (err) {
      setError(
        err instanceof Error ? err.message : 'Failed to submit backtest'
      )
    } finally {
      setLoading(false)
    }
  }

  const inputClass =
    'w-full rounded-lg border border-slate-700 bg-slate-800 px-4 py-3 text-white outline-none focus:border-blue-500'

  return (
    <div className="min-h-screen bg-slate-950 text-white">
      <header className="border-b border-slate-800 px-8 py-5">
        <div className="mx-auto max-w-6xl">
          <h1 className="text-2xl font-bold">Momentum Backtester</h1>
          <p className="mt-1 text-sm text-slate-400">
            Test momentum trading strategies against historical market data.
          </p>
        </div>
      </header>

      <main className="mx-auto max-w-6xl space-y-8 px-8 py-10">
        <section className="rounded-xl border border-slate-800 bg-slate-900 p-6">
          <h2 className="mb-6 text-xl font-semibold">New Backtest</h2>

          <form onSubmit={handleSubmit}>
            <div className="grid gap-5 md:grid-cols-2">
              <div>
                <label htmlFor="symbol" className="mb-2 block text-sm text-slate-300">
                  Stock Symbol
                </label>
                <input
                  id="symbol"
                  type="text"
                  required
                  value={symbol}
                  onChange={(e) => setSymbol(e.target.value)}
                  className={inputClass}
                />
              </div>

              <div>
                <label htmlFor="lookback" className="mb-2 block text-sm text-slate-300">
                  Lookback Period (days)
                </label>
                <input
                  id="lookback"
                  type="number"
                  required
                  min="1"
                  value={lookback}
                  onChange={(e) => setLookback(Number(e.target.value))}
                  className={inputClass}
                />
              </div>

              <div>
                <label htmlFor="start" className="mb-2 block text-sm text-slate-300">
                  Start Date
                </label>
                <input
                  id="start"
                  type="date"
                  required
                  value={start}
                  onChange={(e) => setStart(e.target.value)}
                  className={inputClass}
                />
              </div>

              <div>
                <label htmlFor="end" className="mb-2 block text-sm text-slate-300">
                  End Date
                </label>
                <input
                  id="end"
                  type="date"
                  required
                  min={start}
                  value={end}
                  onChange={(e) => setEnd(e.target.value)}
                  className={inputClass}
                />
              </div>

              <div>
                <label htmlFor="capital" className="mb-2 block text-sm text-slate-300">
                  Initial Capital ($)
                </label>
                <input
                  id="capital"
                  type="number"
                  required
                  min="1"
                  step="any"
                  value={initialCapital}
                  onChange={(e) => setInitialCapital(Number(e.target.value))}
                  className={inputClass}
                />
              </div>
            </div>

            <button
              type="submit"
              disabled={loading}
              className="mt-6 rounded-lg bg-blue-600 px-6 py-3 font-medium transition hover:bg-blue-500 disabled:cursor-not-allowed disabled:opacity-50"
            >
              {loading ? 'Submitting...' : 'Run Backtest'}
            </button>
          </form>
        </section>

        <section className="rounded-xl border border-slate-800 bg-slate-900 p-6">
          <h2 className="mb-6 text-xl font-semibold">Backtest Results</h2>

          {error && (
            <p className="text-red-400">{error}</p>
          )}

          
          {backtest && (
            <div className="space-y-6">
              <div className="space-y-2">
                <p>
                  Backtest ID: <span className="font-semibold">{backtest.id}</span>
                </p>
                <p>
                  Status: <span className="font-semibold">{backtest.status}</span>
                </p>
                {backtest.message && (
                  <p className="text-sm text-slate-400">{backtest.message}</p>
                )}
              </div>

              {backtest.status === 'COMPLETED' && backtest.strategy_metrics && (
                <>
                  <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
                    {[
                      {
                        label: 'Total Return',
                        value: formatPercent(backtest.strategy_metrics.total_return),
                      },
                      {
                        label: 'Sharpe Ratio',
                        value: backtest.strategy_metrics.sharpe_ratio.toFixed(2),
                      },
                      {
                        label: 'Annualized Volatility',
                        value: formatPercent(
                          backtest.strategy_metrics.annualized_volatility
                        ),
                      },
                      {
                        label: 'Maximum Drawdown',
                        value: formatPercent(backtest.strategy_metrics.max_drawdown),
                      },
                    ].map((metric) => (
                      <div
                        key={metric.label}
                        className="rounded-lg border border-slate-700 bg-slate-800 p-4"
                      >
                        <p className="text-sm text-slate-400">{metric.label}</p>
                        <p className="mt-2 text-2xl font-semibold">{metric.value}</p>
                      </div>
                    ))}
                  </div>

                  <div className="grid gap-4 sm:grid-cols-2">
                    <div>
                      <p className="text-sm text-slate-400">Final Strategy Equity</p>
                      <p className="mt-1 text-xl font-semibold">
                        ${backtest.final_equity?.toLocaleString('en-US', {
                          minimumFractionDigits: 2,
                          maximumFractionDigits: 2,
                        })}
                      </p>
                    </div>

                    <div>
                      <p className="text-sm text-slate-400">Final Buy-and-Hold Equity</p>
                      <p className="mt-1 text-xl font-semibold">
                        ${backtest.benchmark_final_equity?.toLocaleString('en-US', {
                          minimumFractionDigits: 2,
                          maximumFractionDigits: 2,
                        })}
                      </p>
                    </div>
                  </div>
                </>
              )}
            </div>
          )}


          {!backtest && !error && (
            <p className="text-slate-400">
              Run a backtest to view performance metrics and equity curves.
            </p>
          )}

          {equityError && (
            <p className="mt-6 text-red-400">{equityError}</p>
          )}

          {backtest?.status === 'COMPLETED' && equityData.length > 0 && (
            <div className="mt-8">
              <h3 className="mb-4 text-lg font-semibold">
                Equity Curve
              </h3>

              <div className="h-96 w-full">
                <ResponsiveContainer width="100%" height="100%">
                  <LineChart
                    data={equityData}
                    margin={{ top: 10, right: 20, left: 15, bottom: 10 }}
                  >
                    <CartesianGrid stroke="#334155" strokeDasharray="3 3" />

                    <XAxis
                      dataKey="trading_date"
                      stroke="#94a3b8"
                      tick={{ fontSize: 12 }}
                      minTickGap={40}
                    />

                    <YAxis
                      stroke="#94a3b8"
                      tick={{ fontSize: 12 }}
                      tickFormatter={(value: number) =>
                        `$${value.toLocaleString('en-US')}`
                      }
                      width={85}
                      domain={['auto', 'auto']}
                    />

                    <Tooltip
                      formatter={(value, name) => [
                        typeof value === 'number'
                          ? `$${value.toLocaleString('en-US', {
                              minimumFractionDigits: 2,
                              maximumFractionDigits: 2,
                            })}`
                          : String(value ?? ''),
                        String(name),
                      ]}
                      contentStyle={{
                        backgroundColor: '#1e293b',
                        border: '1px solid #475569',
                        borderRadius: '8px',
                        color: '#ffffff',
                      }}
                    />

                    <Legend />

                    <Line
                      type="monotone"
                      dataKey="equity"
                      name="Momentum Strategy"
                      stroke="#3b82f6"
                      strokeWidth={2}
                      dot={false}
                    />

                    <Line
                      type="monotone"
                      dataKey="benchmark_equity"
                      name="Buy and Hold"
                      stroke="#22c55e"
                      strokeWidth={2}
                      dot={false}
                    />
                  </LineChart>
                </ResponsiveContainer>
              </div>
            </div>
          )}

        </section>
      </main>
    </div>
  )
}

export default App
