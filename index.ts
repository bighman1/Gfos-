/**
 * GFOS TypeScript SDK
 * Global Financial Operating System — Unified Rail Intelligence Client
 *
 * Observes every financial rail category from a single client:
 *   Banking (SWIFT, SEPA, ACH, Fedwire, CHAPS, CIPS)
 *   Remittance Apps (Wise, Western Union, Remitly, WorldRemit)
 *   Mobile Money (M-Pesa, MTN MoMo, Wave, Airtel, GCash, bKash)
 *   Crypto Networks (Solana/USDC, TRON/USDT, Stellar, Bitcoin, Ethereum)
 *   FX Markets (170+ pairs, cross-rail pressure signals)
 *
 * GFOS does not process payments. It watches where money moves.
 *
 * npm install @gfos/sdk
 */

// ─────────────────────────────────────────────
// Enums & Types
// ─────────────────────────────────────────────

export type RailCategory    = 'banking' | 'remittance' | 'mobile_money' | 'crypto' | 'fx';
export type CongestionLevel = 'low' | 'medium' | 'high';
export type LiquiditySignal = 'deep' | 'moderate' | 'shallow' | 'dry';
export type VolumeSignal    = 'surging' | 'rising' | 'stable' | 'declining' | 'draining';
export type Period          = '1d' | '7d' | '30d' | '90d';

// ─────────────────────────────────────────────
// Intelligence Models
// ─────────────────────────────────────────────

/** A single rail's share of flow on a corridor */
export interface RailShare {
  rail: string;
  category: RailCategory;
  sharePct: number;
  volumeSignal: VolumeSignal;
  trend: 'rising' | 'stable' | 'declining';
}

/** Full corridor intelligence — all rail categories */
export interface CorridorIntelligence {
  sourceCountry: string;
  destinationCountry: string;
  dominantRail: string;
  volumeTrend: string;
  volumeSignal: VolumeSignal;
  volumeChangePct: number;
  congestionLevel: CongestionLevel;
  liquiditySignal: LiquiditySignal;
  /** All observed rails ranked by share — banking, remittance, mobile, crypto */
  railBreakdown: RailShare[];
  aiForecast?: string;
  observedAt: string;
}

/** Single row in a cross-rail comparison */
export interface RailComparisonRow {
  name: string;
  category: RailCategory;
  volumeIndex: number;
  feeIndex: number;
  congestionLevel: CongestionLevel;
  avgSpeed: string;        // e.g. "~10 seconds", "2-5 days"
  volumeSignal: VolumeSignal;
  signal: string;
  trend: 'rising' | 'stable' | 'declining';
}

/** Side-by-side comparison of rails on a corridor — mix any categories */
export interface RailComparison {
  sourceCountry: string;
  destinationCountry: string;
  rails: RailComparisonRow[];
  comparedAt: string;
}

/** Live intelligence for any single rail */
export interface RailIntelligence {
  rail: string;
  category: RailCategory;
  volumeChangePct: number;
  volumeSignal: VolumeSignal;
  congestionLevel: CongestionLevel;
  liquiditySignal: LiquiditySignal;
  feeTrend: string;
  activeCorridors: string[];
  signal: string;
  observedAt: string;
}

/** Global liquidity heatmap — all categories */
export interface HeatmapSnapshot {
  hotspots: Array<{ corridor: string; intensity: number }>;
  coldZones: Array<{ corridor: string; intensity: number }>;
  shifts: Array<{ corridor: string; changePct: number; direction: 'inflow' | 'outflow' }>;
  byCategory: Record<RailCategory, Array<{ corridor: string; intensity: number }>>;
  generatedAt: string;
}

/** Historical flow data for any rail */
export interface RailHistory {
  rail: string;
  category: RailCategory;
  days: number;
  peakDays: string[];
  peakHours: number[];
  avgVolumeIndex: number;
  correlation: Record<string, number>;
  seasonality?: string;
  dataPoints: number;
}

/** FX intelligence with cross-rail pressure detection */
export interface FXSignal {
  pair: string;
  rate: number;
  spreadSignal: 'normal' | 'widening' | 'stressed';
  parallelMarketDivergence?: number;
  crossRailPressure: string;
  observedAt: string;
}

/** Live update from WebSocket stream */
export interface RailUpdate {
  rail: string;
  category: RailCategory;
  volumeChangePct: number;
  congestionLevel: CongestionLevel;
  signal: string;
  timestamp: string;
}

// ─────────────────────────────────────────────
// Client Options
// ─────────────────────────────────────────────

export interface GFOSClientOptions {
  apiKey?: string;
  baseUrl?: string;
}

export interface CompareOptions {
  source: string;
  destination: string;
  rails?: string[];
}

export interface SurgingOptions {
  threshold?: number;
  categories?: RailCategory[];
}

// ─────────────────────────────────────────────
// Sub-clients
// ─────────────────────────────────────────────

class RailsClient {
  constructor(private readonly req: Requester) {}

  /** Get live intelligence for any rail — banking, remittance, mobile, crypto */
  async get(rail: string): Promise<RailIntelligence> {
    const data = await this.req.get(`/rails/${encodeURIComponent(rail)}/intelligence`);
    return this.parse(data);
  }

  /**
   * Returns rails surging above threshold — across ALL categories simultaneously.
   *
   * @example
   * const surging = await client.rails.surging({ threshold: 0.15 });
   * surging.forEach(r => console.log(r.rail, r.category, r.volumeChangePct, r.signal));
   *
   * // Wave          mobile_money  +47%  fastest-growing mobile rail
   * // USDT/TRON     crypto        +29%  remittance substitution
   * // CIPS          banking       +61%  trade finance expansion
   * // Remitly       remittance    +18%  post-payday spike
   */
  async surging(options: SurgingOptions = {}): Promise<RailIntelligence[]> {
    const params = new URLSearchParams();
    params.set('threshold', String(options.threshold ?? 0.15));
    if (options.categories?.length) params.set('categories', options.categories.join(','));
    const data = await this.req.get(`/rails/surging?${params}`);
    return data.rails.map(this.parse);
  }

  /** All rails currently showing congestion */
  async congested(): Promise<RailIntelligence[]> {
    const data = await this.req.get('/rails/congested');
    return data.rails.map(this.parse);
  }

  /**
   * All observed rails in a category.
   *
   * @example
   * const bankingRails    = await client.rails.byCategory('banking');
   * const mobileRails     = await client.rails.byCategory('mobile_money');
   * const remittanceRails = await client.rails.byCategory('remittance');
   * const cryptoRails     = await client.rails.byCategory('crypto');
   */
  async byCategory(category: RailCategory): Promise<RailIntelligence[]> {
    const data = await this.req.get(`/rails/category/${category}`);
    return data.rails.map(this.parse);
  }

  /** Historical flow data for any rail — up to 365 days */
  async history(rail: string, days = 30): Promise<RailHistory> {
    const data = await this.req.get(`/rails/${encodeURIComponent(rail)}/history?days=${days}`);
    return {
      rail: data.rail,
      category: data.category as RailCategory,
      days: data.days,
      peakDays: data.peak_days,
      peakHours: data.peak_hours,
      avgVolumeIndex: data.avg_volume_index,
      correlation: data.correlation,
      seasonality: data.seasonality,
      dataPoints: data.data_points,
    };
  }

  private parse(d: any): RailIntelligence {
    return {
      rail: d.rail,
      category: d.category as RailCategory,
      volumeChangePct: d.volume_change_pct,
      volumeSignal: d.volume_signal as VolumeSignal,
      congestionLevel: d.congestion_level as CongestionLevel,
      liquiditySignal: d.liquidity_signal as LiquiditySignal,
      feeTrend: d.fee_trend,
      activeCorridors: d.active_corridors,
      signal: d.signal,
      observedAt: d.observed_at,
    };
  }
}

class HeatmapClient {
  constructor(private readonly req: Requester) {}

  /** Global liquidity heatmap — all rail categories */
  async snapshot(): Promise<HeatmapSnapshot> {
    const d = await this.req.get('/heatmap/snapshot');
    return {
      hotspots: d.hotspots,
      coldZones: d.cold_zones,
      shifts: d.shifts,
      byCategory: d.by_category,
      generatedAt: d.generated_at,
    };
  }
}

class FXClient {
  constructor(private readonly req: Requester) {}

  /**
   * FX intelligence for a currency pair — includes cross-rail pressure signals.
   *
   * @example
   * const signal = await client.fx.signal('USD/KES');
   * console.log(signal.spreadSignal);              // 'widening'
   * console.log(signal.parallelMarketDivergence);  // 4.2
   * console.log(signal.crossRailPressure);         // 'crypto absorbing informal demand'
   */
  async signal(pair: string): Promise<FXSignal> {
    const d = await this.req.get(`/fx/${encodeURIComponent(pair)}/signal`);
    return {
      pair: d.pair,
      rate: d.rate,
      spreadSignal: d.spread_signal,
      parallelMarketDivergence: d.parallel_market_divergence,
      crossRailPressure: d.cross_rail_pressure,
      observedAt: d.observed_at,
    };
  }
}

class StreamClient {
  private readonly wsBase: string;
  private readonly apiKey: string;

  constructor(baseUrl: string, apiKey: string) {
    this.wsBase  = baseUrl.replace('https://', 'wss://').replace('http://', 'ws://');
    this.apiKey  = apiKey;
  }

  /** Stream live updates from ALL rails, all categories */
  all(): Emitter<RailUpdate> {
    return this.connect(`/v1/stream/rails/all`);
  }

  /** Stream specific rails */
  rails(railIds: string[]): Emitter<RailUpdate> {
    return this.connect(`/v1/stream/rails?rails=${railIds.join(',')}`);
  }

  /** Stream all rails in a category */
  category(cat: RailCategory): Emitter<RailUpdate> {
    return this.connect(`/v1/stream/category/${cat}`);
  }

  private connect(path: string): Emitter<RailUpdate> {
    const emitter = new Emitter<RailUpdate>();
    const ws = new WebSocket(`${this.wsBase}${path}&key=${this.apiKey}`);
    ws.onmessage = ({ data }) => {
      try { emitter.emit('update', JSON.parse(data)); } catch {}
    };
    ws.onerror = (e) => emitter.emit('error', e as any);
    ws.onclose = () => emitter.emit('close', null as any);
    return emitter;
  }
}

// ─────────────────────────────────────────────
// Main Client
// ─────────────────────────────────────────────

export class GFOSClient {
  /**
   * GFOS TypeScript SDK — Unified Rail Intelligence Client
   *
   * @example
   * const client = new GFOSClient({ apiKey: 'gfos_live_...' });
   *
   * // Full corridor picture — all rails
   * const intel = await client.corridor('KE', 'DE');
   * console.log(intel.dominantRail);   // 'M-Pesa → USDC/Solana → SEPA'
   * console.log(intel.railBreakdown);  // all rails ranked by share
   *
   * // Side-by-side comparison
   * const cmp = await client.compare({ source: 'KE', destination: 'DE' });
   * cmp.rails.forEach(r => console.log(r.name, r.volumeIndex, r.feeIndex, r.avgSpeed));
   *
   * // Surging rails across all categories
   * const surging = await client.rails.surging({ threshold: 0.15 });
   *
   * // Stream everything live
   * client.stream.all().on('update', u => console.log(`[${u.category}] ${u.rail}: ${u.signal}`));
   */

  readonly rails:   RailsClient;
  readonly heatmap: HeatmapClient;
  readonly fx:      FXClient;
  readonly stream:  StreamClient;

  private readonly req: Requester;

  constructor(options: GFOSClientOptions = {}) {
    const apiKey = options.apiKey
      ?? (typeof process !== 'undefined' ? process.env.GFOS_API_KEY : undefined);
    if (!apiKey) throw new Error('No API key. Pass apiKey: or set GFOS_API_KEY env var.');

    const baseUrl = options.baseUrl ?? 'https://api.gfos.io/v1';
    this.req     = new Requester(baseUrl, apiKey);
    this.rails   = new RailsClient(this.req);
    this.heatmap = new HeatmapClient(this.req);
    this.fx      = new FXClient(this.req);
    this.stream  = new StreamClient(baseUrl, apiKey);
  }

  /**
   * Full corridor intelligence — across ALL rail categories.
   *
   * Returns dominant rail, volume trend, full rail breakdown (all categories),
   * and AI forecast.
   */
  async corridor(source: string, destination: string, period: Period = '7d'): Promise<CorridorIntelligence> {
    const d = await this.req.get(`/corridors/${source}-${destination}/intelligence?period=${period}`);
    return {
      sourceCountry: d.source_country,
      destinationCountry: d.destination_country,
      dominantRail: d.dominant_rail,
      volumeTrend: d.volume_trend,
      volumeSignal: d.volume_signal as VolumeSignal,
      volumeChangePct: d.volume_change_pct,
      congestionLevel: d.congestion_level as CongestionLevel,
      liquiditySignal: d.liquidity_signal as LiquiditySignal,
      railBreakdown: d.rail_breakdown.map((r: any) => ({
        rail: r.rail,
        category: r.category as RailCategory,
        sharePct: r.share_pct,
        volumeSignal: r.volume_signal as VolumeSignal,
        trend: r.trend,
      })),
      aiForecast: d.ai_forecast,
      observedAt: d.observed_at,
    };
  }

  /**
   * Compare any mix of rails side-by-side on a corridor.
   * Mix categories freely — SWIFT vs Wise vs M-Pesa vs USDC/Solana on the same screen.
   */
  async compare(options: CompareOptions): Promise<RailComparison> {
    const params = new URLSearchParams();
    if (options.rails?.length) params.set('rails', options.rails.join(','));
    const d = await this.req.get(
      `/corridors/${options.source}-${options.destination}/rails/compare?${params}`
    );
    return {
      sourceCountry: d.source_country,
      destinationCountry: d.destination_country,
      rails: d.rails.map((r: any) => ({
        name: r.name,
        category: r.category as RailCategory,
        volumeIndex: r.volume_index,
        feeIndex: r.fee_index,
        congestionLevel: r.congestion_level as CongestionLevel,
        avgSpeed: r.avg_speed,
        volumeSignal: r.volume_signal as VolumeSignal,
        signal: r.signal,
        trend: r.trend,
      })),
      comparedAt: d.compared_at,
    };
  }

  /** Submit a rail observation to the community intelligence layer */
  async reportObservation(options: {
    rail: string;
    source: string;
    destination: string;
    congestionObserved: boolean;
    feeIndex?: number;
    notes?: string;
  }): Promise<{ accepted: boolean }> {
    return this.req.post('/report-observation', {
      rail: options.rail,
      source: options.source,
      destination: options.destination,
      congestion_observed: options.congestionObserved,
      fee_index: options.feeIndex,
      notes: options.notes,
    });
  }
}

// ─────────────────────────────────────────────
// Internal Helpers
// ─────────────────────────────────────────────

class Requester {
  constructor(private readonly baseUrl: string, private readonly apiKey: string) {}

  async get(path: string): Promise<any> {
    const res = await fetch(`${this.baseUrl}${path}`, { headers: this.headers() });
    if (!res.ok) throw new GFOSError(res.status, (await res.json().catch(() => ({}))).message ?? res.statusText);
    return res.json();
  }

  async post(path: string, body: unknown): Promise<any> {
    const res = await fetch(`${this.baseUrl}${path}`, {
      method: 'POST', headers: this.headers(), body: JSON.stringify(body),
    });
    if (!res.ok) throw new GFOSError(res.status, (await res.json().catch(() => ({}))).message ?? res.statusText);
    return res.json();
  }

  private headers() {
    return {
      Authorization: `Bearer ${this.apiKey}`,
      'Content-Type': 'application/json',
      'X-SDK-Version': '0.1.0',
    };
  }
}

class Emitter<T> {
  private listeners: Record<string, Array<(d: T) => void>> = {};
  on(event: string, cb: (d: T) => void): this { (this.listeners[event] ??= []).push(cb); return this; }
  emit(event: string, d: T): void { this.listeners[event]?.forEach(cb => cb(d)); }
}

export class GFOSError extends Error {
  constructor(public readonly statusCode: number, message: string) {
    super(`GFOS API Error ${statusCode}: ${message}`);
    this.name = 'GFOSError';
  }
}
