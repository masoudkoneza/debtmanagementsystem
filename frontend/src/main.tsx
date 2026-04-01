/**
 * main.tsx — Application entry point.
 *
 * Wraps the app in three providers, in order from outermost to innermost:
 *
 *  1. <Provider store={store}>
 *     Makes the Redux store available to every component via useSelector /
 *     useDispatch without prop drilling.
 *
 *  2. <BrowserRouter>
 *     Enables HTML5 history-based routing (clean URLs without hash fragments).
 *     Must wrap everything that uses <Routes>, <Link>, or useNavigate.
 *
 *  3. <App />
 *     The route tree and all page components.
 *
 * React.StrictMode is enabled to surface potential issues during development
 * (double-invocation of effects, deprecated API usage, etc.).  It has no
 * effect in production builds.
 */

import React from 'react';
import ReactDOM from 'react-dom/client';
import { Provider } from 'react-redux';
import { BrowserRouter } from 'react-router-dom';
import { store } from './store/store';
import App from './App';

// Ant Design's default global styles.
// Import here rather than in index.html so the CSS is tree-shaken with the
// rest of the bundle in production.
import 'antd/dist/reset.css';

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    {/* Redux store — must be the outermost wrapper so all components can dispatch */}
    <Provider store={store}>
      {/* React Router — must wrap App so <Routes> and navigation hooks work */}
      <BrowserRouter>
        <App />
      </BrowserRouter>
    </Provider>
  </React.StrictMode>
);
