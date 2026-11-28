

import { useState } from 'react'
import {
  LayoutDashboard, FolderOpen, Search, Settings, ShieldCheck, Sparkles,
  FileText, FileImage, FileSpreadsheet, Clock3, Star, Trash2, Plus,
  ChevronRight, ChevronDown, HardDrive, ScanSearch, ArrowUpRight, Menu,
  X, SlidersHorizontal, Activity, LockKeyhole, CheckCircle2, CircleHelp,
  Files
} from 'lucide-react'
import './App.css'

function App() {
  const [activePage, setActivePage] = useState('Overview')
  const [search, setSearch] = useState('')
 const [sidebarOpen, setSidebarOpen] = useState(() => window.innerWidth > 760)

  const menuItems = [
    { name: 'Overview', icon: LayoutDashboard },
    { name: 'Search', icon: Search },
    { name: 'Indexed Files', icon: FolderOpen },
    { name: 'Scan Policies', icon: ScanSearch },
  ]

  const libraryItems = [
    { name: 'Recent files', icon: Clock3 },
    { name: 'Starred', icon: Star },
    { name: 'Trash', icon: Trash2 },
  ]


  const handleSearch = () => {
    if (search.trim()) {
      setActivePage('Search')
    }
  }

 const navigate = (page) => {
  setActivePage(page)

  if (window.innerWidth <= 760) {
    setSidebarOpen(false)
  }
}
  

  const renderSearch = () => (
    <div className="ai-search-panel">
      <div className="ai-heading">
        <div className="ai-icon">
          <Sparkles size={21} />
        </div>
        <div>
          <span className="eyebrow">YOUR AI FILE ASSISTANT</span>
          <h2>Ask Sift anything.</h2>
          <p>Find information, understand documents and discover connections across your files.</p>
        </div>
      </div>

      <div className="ai-input-wrapper">
        <textarea
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          onKeyDown={(e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
              e.preventDefault()
              handleSearch()
            }
          }}
          placeholder="Ask a question about your files..."
          rows={2}
        />
        <div className="ai-input-bottom">
          <span><LockKeyhole size={13} /> Your files stay on your device</span>
          <button className="ai-submit" onClick={handleSearch}>
            Ask Sift <ArrowUpRight size={16} />
          </button>
        </div>
      </div>

      <div className="suggestions">
        <span className="suggestion-label">TRY ASKING</span>
        <div className="suggestion-list">
          {[
            'Summarise my lecture notes',
            'Find my recent project files',
            'What do my documents say about AI?'
          ].map((item) => (
            <button
              key={item}
              className="suggestion-chip"
              onClick={() => setSearch(item)}
            >
              <Sparkles size={13} /> {item}
            </button>
          ))}
        </div>
      </div>
    </div>
  )

  const renderOverview = () => (
    <>
      <section className="welcome-section">
        <div>
          <span className="eyebrow">YOUR PERSONAL FILE INTELLIGENCE</span>
          <h1>Your files. <span>Understood.</span></h1>
          <p>Welcome to your workspace. Everything you need to find, manage and understand your files.</p>
        </div>

        <div className="welcome-date">
          <div className="welcome-date-icon">
            <Activity size={18} />
          </div>
          <div>
            <strong>Workspace status</strong>
            <span><i className="online-dot" /> Ready to discover</span>
          </div>
        </div>
      </section>

      {renderSearch()}

      <section className="stats-grid">
        <div className="stat-card">
          <div className="stat-top">
            <span>Indexed files</span>
            <div className="stat-icon teal"><Files size={19} /></div>
          </div>
          <h2>0</h2>
          <p>Files in your local index</p>
          <span className="stat-foot">Waiting for your first scan</span>
        </div>

        <div className="stat-card">
          <div className="stat-top">
            <span>Scanned folders</span>
            <div className="stat-icon yellow"><FolderOpen size={19} /></div>
          </div>
          <h2>0</h2>
          <p>Folders connected to Sift</p>
          <span className="stat-foot">No folders configured yet</span>
        </div>

        <div className="stat-card">
          <div className="stat-top">
            <span>Storage used</span>
            <div className="stat-icon grey"><HardDrive size={19} /></div>
          </div>
          <h2>0 <small>GB</small></h2>
          <p>Space occupied by indexed files</p>
          <span className="stat-foot">Your device storage</span>
        </div>
      </section>

      <section className="content-grid">
        <div className="content-main">
          <div className="section-heading">
            <div>
              <h2>Quick actions</h2>
              <p>Get more out of your workspace.</p>
            </div>
          </div>

          <div className="quick-actions">
            <button className="quick-card" onClick={() => navigate('Scan Policies')}>
              <div className="quick-icon teal"><ScanSearch size={21} /></div>
              <div>
                <h3>Scan a folder</h3>
                <p>Choose folders for Sift to index and understand.</p>
              </div>
              <ChevronRight size={18} />
            </button>

            <button className="quick-card" onClick={() => navigate('Indexed Files')}>
              <div className="quick-icon yellow"><FolderOpen size={21} /></div>
              <div>
                <h3>Explore your files</h3>
                <p>Browse and manage your indexed documents.</p>
              </div>
              <ChevronRight size={18} />
            </button>

            <button className="quick-card" onClick={() => navigate('Search')}>
              <div className="quick-icon purple"><Sparkles size={21} /></div>
              <div>
                <h3>Ask Sift AI</h3>
                <p>Get answers from the information in your files.</p>
              </div>
              <ChevronRight size={18} />
            </button>
          </div>
        </div>

        <div className="privacy-panel">
          <div className="privacy-icon"><ShieldCheck size={23} /></div>
          <span className="eyebrow">YOUR PRIVACY MATTERS</span>
          <h3>Your files stay yours.</h3>
          <p>Sift is designed around local file processing. Your documents remain under your control.</p>
          <div className="privacy-divider" />
          <div className="privacy-detail">
            <CheckCircle2 size={16} />
            <span>Local-first architecture</span>
          </div>
          <div className="privacy-detail">
            <CheckCircle2 size={16} />
            <span>You control indexed folders</span>
          </div>
          <div className="privacy-detail">
            <CheckCircle2 size={16} />
            <span>Privacy-conscious design</span>
          </div>
        </div>
      </section>

      <section className="recent-section">
        <div className="section-heading">
          <div>
            <h2>Recent files</h2>
            <p>Your latest indexed documents will appear here.</p>
          </div>
          <button className="text-button" onClick={() => navigate('Indexed Files')}>
            View all <ArrowUpRight size={15} />
          </button>
        </div>

        <div className="empty-state">
          <div className="empty-icon"><FolderOpen size={25} /></div>
          <h3>Your workspace is waiting.</h3>
          <p>Once you scan a folder, your files will appear here.</p>
          <button className="primary-button" onClick={() => navigate('Scan Policies')}>
            <Plus size={16} /> Add your first folder
          </button>
        </div>
      </section>
    </>
  )

  const renderSearchPage = () => (
    <div className="page-content">
      <div className="page-intro">
        <span className="eyebrow">INTELLIGENT DISCOVERY</span>
        <h1>Search your knowledge.</h1>
        <p>Ask questions in everyday language. Sift helps you find information across your indexed files.</p>
      </div>
      {renderSearch()}
      <div className="search-info">
        <ShieldCheck size={19} />
        <div>
          <strong>Search with confidence</strong>
          <p>Search is designed to work with your locally indexed content. Results will be connected when the local search API is integrated.</p>
        </div>
      </div>
    </div>
  )

  const renderFilesPage = () => (
    <div className="page-content">
      <div className="page-intro page-intro-row">
        <div>
          <span className="eyebrow">YOUR DOCUMENT LIBRARY</span>
          <h1>Indexed files</h1>
          <p>Explore the documents Sift has indexed on your device.</p>
        </div>
        <button className="primary-button" onClick={() => navigate('Scan Policies')}>
          <Plus size={16} /> Add folder
        </button>
      </div>

      <div className="file-toolbar">
        <div className="file-search">
          <Search size={17} />
          <input placeholder="Filter your files..." />
        </div>
        <button className="filter-button"><SlidersHorizontal size={16} /> Filters</button>
      </div>

      <div className="file-table">
        <div className="file-table-header">
          <span>Name</span>
          <span>Type</span>
          <span>Size</span>
          <span>Last modified</span>
          <span></span>
        </div>

        <div className="file-empty">
          <FolderOpen size={30} />
          <h3>No indexed files yet</h3>
          <p>Scan a folder to start building your searchable library.</p>
          <button className="primary-button" onClick={() => navigate('Scan Policies')}>
            <Plus size={16} /> Configure a folder
          </button>
        </div>
      </div>
    </div>
  )

  const renderScanPage = () => (
    <div className="page-content">
      <div className="page-intro">
        <span className="eyebrow">LOCAL FILE INDEXING</span>
        <h1>Scan policies</h1>
        <p>Choose which folders Sift can access and index for intelligent discovery.</p>
      </div>

      <div className="scan-intro-card">
        <div className="scan-icon"><ScanSearch size={25} /></div>
        <div>
          <h2>Build your personal knowledge library.</h2>
          <p>Connect folders on your device. Sift can then organise and index supported files for search.</p>
        </div>
      </div>

      <div className="scan-empty">
        <div className="empty-icon"><FolderOpen size={28} /></div>
        <h3>No folders configured</h3>
        <p>You haven't selected any folders for scanning yet.</p>
        <button className="primary-button" onClick={() => alert('Folder selection will be connected to your local backend.')}>
          <Plus size={16} /> Select a folder
        </button>
        <span className="helper-text">Folder selection requires integration with your local file system API.</span>
      </div>

      <div className="info-card">
        <ShieldCheck size={20} />
        <div>
          <strong>You're in control</strong>
          <p>Only folders you explicitly select should be indexed. You can change your scan policies at any time.</p>
        </div>
      </div>
    </div>
  )

  const renderSettingsPage = () => (
    <div className="page-content">
      <div className="page-intro">
        <span className="eyebrow">PERSONALISE YOUR WORKSPACE</span>
        <h1>Settings</h1>
        <p>Manage your Sift workspace preferences and privacy.</p>
      </div>

      <div className="settings-card">
        <div className="settings-row">
          <div className="settings-icon"><ShieldCheck size={19} /></div>
          <div>
            <strong>Privacy and security</strong>
            <p>Review your local processing and file access preferences.</p>
          </div>
          <span className="settings-status">Local-first</span>
        </div>
        <div className="settings-row">
          <div className="settings-icon"><HardDrive size={19} /></div>
          <div>
            <strong>Storage preferences</strong>
            <p>Manage your indexed content and storage information.</p>
          </div>
          <ChevronRight size={18} />
        </div>
        <div className="settings-row">
          <div className="settings-icon"><Activity size={19} /></div>
          <div>
            <strong>Indexing preferences</strong>
            <p>Manage how and when your files are scanned.</p>
          </div>
          <ChevronRight size={18} />
        </div>
      </div>
    </div>
  )

  const pageContent = {
    'Overview': renderOverview,
    'Search': renderSearchPage,
    'Indexed Files': renderFilesPage,
    'Scan Policies': renderScanPage,
    'Settings': renderSettingsPage,
  }

  return (
    <div className="app-container">
      {sidebarOpen && (
        <div className="mobile-overlay" onClick={() => setSidebarOpen(false)} />
      )}

      <aside className={`sidebar ${sidebarOpen ? 'sidebar-open' : 'sidebar-closed'}`}>
        <div className="brand">
          <div className="brand-icon"><Sparkles size={21} /></div>
          <div className="brand-name">sift<span>.</span></div>
          <button className="close-sidebar" onClick={() => setSidebarOpen(false)}>
            <X size={18} />
          </button>
        </div>

        <div className="workspace-switcher">
          <div className="workspace-avatar">S</div>
          <div>
            <strong>Personal workspace</strong>
            <span>Local device</span>
          </div>
          <ChevronDown size={15} />
        </div>

        <div className="sidebar-group">
          <span className="menu-label">WORKSPACE</span>
          <nav>
            {menuItems.map((item) => {
              const Icon = item.icon
              return (
                <button
                  key={item.name}
                  className={`nav-item ${activePage === item.name ? 'active' : ''}`}
                  onClick={() => navigate(item.name)}
                >
                  <Icon size={18} />
                  <span>{item.name}</span>
                  {activePage === item.name && <span className="active-indicator" />}
                </button>
              )
            })}
          </nav>
        </div>

        <div className="sidebar-group library-group">
          <span className="menu-label">YOUR LIBRARY</span>
          <nav>
            {libraryItems.map((item) => {
              const Icon = item.icon
              return (
                <button
                  key={item.name}
                  className={`nav-item ${activePage === item.name ? 'active' : ''}`}
                  onClick={() => navigate(item.name)}
                >
                  <Icon size={18} />
                  <span>{item.name}</span>
                </button>
              )
            })}
          </nav>
        </div>

        <div className="sidebar-bottom">
          <div className="privacy-card">
            <div className="privacy-card-top">
              <ShieldCheck size={19} />
              <span>PRIVACY FIRST</span>
            </div>
            <h4>Your files stay yours.</h4>
            <p>Your files remain under your control. Sift is designed with local-first processing.</p>
            <div className="privacy-status"><span /> Privacy-conscious design</div>
          </div>

          <button className="nav-item settings-link" onClick={() => navigate('Settings')}>
            <Settings size={18} />
            <span>Settings</span>
          </button>

          <div className="sidebar-footer">
            <span>SIFT v1.0</span>
            <span>Made for discovery.</span>
          </div>
        </div>
      </aside>

      <main className="main-content">
        <header className="topbar">
          <div className="topbar-left">
            <button className="menu-toggle" onClick={() => setSidebarOpen(!sidebarOpen)}>
              <Menu size={20} />
            </button>
            <div className="breadcrumb">
              <span>Workspace</span>
              <ChevronRight size={14} />
              <strong>{activePage}</strong>
            </div>
          </div>

          <div className="topbar-right">
            <div className="device-status">
              <span className="online-dot" />
              Local device
            </div>
            <button className="help-button" title="Help"><CircleHelp size={19} /></button>
            <div className="avatar">S</div>
          </div>
        </header>

        <div className="dashboard">
          {pageContent[activePage] ? pageContent[activePage]() : (
            <div className="page-content">
              <div className="page-intro">
                <span className="eyebrow">YOUR LIBRARY</span>
                <h1>{activePage}</h1>
                <p>This section will display your {activePage.toLowerCase()}.</p>
              </div>
              <div className="empty-state">
                <FolderOpen size={30} />
                <h3>Nothing here just yet</h3>
                <p>This feature will be available when the relevant functionality is connected.</p>
                <button className="text-button" onClick={() => navigate('Overview')}>Back to overview</button>
              </div>
            </div>
          )}

          <footer className="app-footer">
            <span>© 2026 Sift</span>
            <span>Built for privacy. Designed for discovery.</span>
          </footer>
        </div>
      </main>
    </div>
  )
}

export default App


