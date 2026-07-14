import { useMemo, useState } from 'react'
import './App.css'
import { API_BASE } from './config'

const TOTAL_PAPERS = 55

/* ─── Inline SVG Icons ──────────────────────────────────────────── */
function IconSearch() {
  return (
    <svg className="search-icon" xmlns="http://www.w3.org/2000/svg" width="20" height="20"
      viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"
      strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
      <circle cx="11" cy="11" r="8" />
      <path d="m21 21-4.35-4.35" />
    </svg>
  )
}

function IconUser() {
  return (
    <svg xmlns="http://www.w3.org/2000/svg" width="13" height="13" viewBox="0 0 24 24"
      fill="none" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round"
      strokeLinejoin="round" aria-hidden="true">
      <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2" />
      <circle cx="12" cy="7" r="4" />
    </svg>
  )
}

function IconBuilding() {
  return (
    <svg xmlns="http://www.w3.org/2000/svg" width="13" height="13" viewBox="0 0 24 24"
      fill="none" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round"
      strokeLinejoin="round" aria-hidden="true">
      <rect x="4" y="2" width="16" height="20" rx="2" ry="2" />
      <path d="M9 22V12h6v10" />
      <path d="M8 6h.01M16 6h.01M8 10h.01M16 10h.01" />
    </svg>
  )
}

function IconExternalLink() {
  return (
    <svg xmlns="http://www.w3.org/2000/svg" width="12" height="12" viewBox="0 0 24 24"
      fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round"
      strokeLinejoin="round" aria-hidden="true">
      <path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6" />
      <polyline points="15 3 21 3 21 9" />
      <line x1="10" y1="14" x2="21" y2="3" />
    </svg>
  )
}

function IconDocument() {
  return (
    <svg className="status-icon" xmlns="http://www.w3.org/2000/svg" width="48" height="48"
      viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5"
      strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
      <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" />
      <polyline points="14 2 14 8 20 8" />
      <line x1="16" y1="13" x2="8" y2="13" />
      <line x1="16" y1="17" x2="8" y2="17" />
      <polyline points="10 9 9 9 8 9" />
    </svg>
  )
}

function IconError() {
  return (
    <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24"
      fill="none" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round"
      strokeLinejoin="round" aria-hidden="true" style={{ flexShrink: 0, marginTop: '1px' }}>
      <circle cx="12" cy="12" r="10" />
      <line x1="12" y1="8" x2="12" y2="12" />
      <line x1="12" y1="16" x2="12.01" y2="16" />
    </svg>
  )
}

/* ─── Degree Badge ──────────────────────────────────────────────── */
function DegreeBadge({ type }) {
  const classMap = { BSc: 'degree-bsc', MSc: 'degree-msc', PhD: 'degree-phd', 'N/A': 'degree-na' }
  const cls = classMap[type] || 'degree-na'
  return <span className={`degree-badge ${cls}`}>{type}</span>
}

/* ─── Result Card ───────────────────────────────────────────────── */
function ResultCard({ paper }) {
  const keywords = paper.keywords
    ? paper.keywords.split(',').map((k) => k.trim()).filter(Boolean)
    : []

  // Clamp score between 0–1 for the progress bar
  const score = paper.relevance_score ?? 0
  const fillPct = `${Math.min(score * 100, 100).toFixed(1)}%`

  return (
    <li className="result-card">
      {/* Top: degree badge + year */}
      <div className="card-badges">
        <DegreeBadge type={paper.degree_type} />
        <span className="year-badge">{paper.year}</span>
      </div>

      {/* Title */}
      <h3 className="result-title">{paper.title}</h3>

      {/* Authors */}
      <p className="result-authors">
        <IconUser />
        {paper.authors}
      </p>

      {/* Institution row */}
      <div className="card-institution">
        <IconBuilding />
        <span className="institution-name">{paper.university}</span>
        <span className="institution-sep" aria-hidden="true">|</span>
        <span className="institution-dept">{paper.department}</span>
      </div>

      {/* Abstract */}
      <p className="result-abstract">{paper.abstract}</p>

      {/* Keyword tags */}
      {keywords.length > 0 && (
        <ul className="tag-list" aria-label="Keywords">
          {keywords.map((kw) => (
            <li key={kw} className="tag">{kw}</li>
          ))}
        </ul>
      )}

      {/* Footer: relevance score + source link */}
      <div className="card-footer">
        {score > 0 && (
          <div className="relevance-wrapper" title={`Relevance score: ${score.toFixed(4)}`}>
            <span className="relevance-label">Relevance</span>
            <div className="relevance-track" role="progressbar"
              aria-valuenow={Math.round(score * 100)}
              aria-valuemin={0} aria-valuemax={100}>
              <div className="relevance-fill" style={{ width: fillPct }} />
            </div>
            <span className="relevance-value">{score.toFixed(3)}</span>
          </div>
        )}

        {paper.source_url && (
          <a href={paper.source_url} target="_blank" rel="noopener noreferrer"
            className="source-link">
            View Paper <IconExternalLink />
          </a>
        )}
      </div>
    </li>
  )
}

/* ─── Main App ──────────────────────────────────────────────────── */
function App() {
  const [query, setQuery]               = useState('')
  const [results, setResults]           = useState([])
  const [loading, setLoading]           = useState(false)
  const [error, setError]               = useState(null)
  const [hasSearched, setHasSearched]   = useState(false)
  const [universityFilter, setUniversityFilter] = useState('')
  const [degreeFilter, setDegreeFilter] = useState('')

  const universities = useMemo(
    () => [...new Set(results.map((p) => p.university))].sort(),
    [results],
  )
  const degreeTypes = useMemo(
    () => [...new Set(results.map((p) => p.degree_type))].sort(),
    [results],
  )

  const filteredResults = useMemo(
    () =>
      results.filter(
        (p) =>
          (!universityFilter || p.university === universityFilter) &&
          (!degreeFilter || p.degree_type === degreeFilter),
      ),
    [results, universityFilter, degreeFilter],
  )

  async function handleSearch(e) {
    e.preventDefault()
    const trimmed = query.trim()
    if (!trimmed) return

    setLoading(true)
    setError(null)
    setHasSearched(true)
    setUniversityFilter('')
    setDegreeFilter('')

    try {
      const res = await fetch(
        `${API_BASE}/api/search/?q=${encodeURIComponent(trimmed)}&limit=20`,
      )
      if (!res.ok) throw new Error(`Request failed with status ${res.status}`)
      const data = await res.json()
      setResults(Array.isArray(data) ? data : [])
    } catch {
      setError(
        `Could not reach the search service. Is the backend running on ${API_BASE}?`,
      )
      setResults([])
    } finally {
      setLoading(false)
    }
  }

  const isFiltered = universityFilter !== '' || degreeFilter !== ''

  return (
    <div className="app">

      {/* ── Hero / Search Header ─────────────────────────────── */}
      <header className="hero">
        <div className="hero-inner">
          <div className="hero-badge" aria-label="Course context">
            CSC 522 &nbsp;·&nbsp; Information Retrieval System
          </div>

          <h1 className="hero-title">
            Nigerian Research&nbsp;<span>IR</span>
          </h1>

          <p className="hero-subtitle">
            Search across {TOTAL_PAPERS} academic research papers from Nigerian universities
          </p>

          <form className="search-form" onSubmit={handleSearch} role="search"
            aria-label="Search research papers">
            <div className="search-input-wrapper">
              <IconSearch />
              <input
                id="main-search"
                type="search"
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                placeholder="Search by topic, author, keyword, or abstract…"
                aria-label="Search query"
                autoComplete="off"
                spellCheck="false"
              />
            </div>
            <button type="submit" className="search-btn"
              disabled={loading || !query.trim()}
              aria-busy={loading}>
              {loading ? 'Searching…' : 'Search'}
            </button>
          </form>
        </div>
      </header>

      {/* ── Main Content ─────────────────────────────────────── */}
      <main className="main-content" id="results" aria-live="polite">

        {/* Error state */}
        {error && (
          <div className="error-message" role="alert">
            <IconError />
            <span>{error}</span>
          </div>
        )}

        {/* Toolbar: result count + filters */}
        {!error && hasSearched && results.length > 0 && (
          <div className="results-toolbar">
            <span className="results-count">
              <strong>{filteredResults.length}</strong>
              &nbsp;result{filteredResults.length !== 1 ? 's' : ''}
              {isFiltered ? ' (filtered)' : ` for "${query.trim()}"`}
            </span>

            <div className="filters" role="group" aria-label="Filter results">
              <div className="filter-group">
                <span className="filter-label" id="univ-label">University</span>
                <select
                  value={universityFilter}
                  onChange={(e) => setUniversityFilter(e.target.value)}
                  aria-labelledby="univ-label">
                  <option value="">All</option>
                  {universities.map((u) => (
                    <option key={u} value={u}>{u}</option>
                  ))}
                </select>
              </div>

              <div className="filter-group">
                <span className="filter-label" id="deg-label">Degree</span>
                <select
                  value={degreeFilter}
                  onChange={(e) => setDegreeFilter(e.target.value)}
                  aria-labelledby="deg-label">
                  <option value="">All</option>
                  {degreeTypes.map((d) => (
                    <option key={d} value={d}>{d}</option>
                  ))}
                </select>
              </div>
            </div>
          </div>
        )}

        {/* Loading */}
        {!error && loading && (
          <div className="status-message">
            <p>Searching across {TOTAL_PAPERS} papers…</p>
          </div>
        )}

        {/* Landing / empty prompt */}
        {!error && !loading && !hasSearched && (
          <div className="status-message">
            <IconDocument />
            <p>Enter a topic, keyword, or author name to begin</p>
            <p className="status-hint">
              Try: <em>"machine learning"</em>, <em>"bioinformatics"</em>, <em>"cybersecurity"</em>
            </p>
          </div>
        )}

        {/* No results */}
        {!error && !loading && hasSearched && results.length === 0 && (
          <div className="status-message">
            <IconDocument />
            <p>No results found for <em>"{query}"</em></p>
            <p className="status-hint">Try different keywords or a shorter phrase</p>
          </div>
        )}

        {/* Filters zeroed out results */}
        {!error && !loading && hasSearched && results.length > 0 && filteredResults.length === 0 && (
          <div className="status-message">
            <p>No results match the selected filters</p>
            <p className="status-hint">Try adjusting or clearing the dropdowns above</p>
          </div>
        )}

        {/* Result cards */}
        {!error && !loading && filteredResults.length > 0 && (
          <ul className="results-list" aria-label="Search results">
            {filteredResults.map((paper) => (
              <ResultCard key={paper.id} paper={paper} />
            ))}
          </ul>
        )}
      </main>

      {/* ── Footer ───────────────────────────────────────────── */}
      <footer className="page-footer">
        Nigerian Research IR &nbsp;·&nbsp; CSC 522 Project &nbsp;·&nbsp;
        {TOTAL_PAPERS} papers indexed &nbsp;·&nbsp; TF-IDF + Cosine Similarity
      </footer>

    </div>
  )
}

export default App
