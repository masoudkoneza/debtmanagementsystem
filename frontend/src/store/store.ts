/**
 * store.ts — Redux store configuration.
 *
 * Uses Redux Toolkit's configureStore which:
 *  - Automatically sets up Redux DevTools Extension support.
 *  - Adds thunk middleware by default (needed for async actions later).
 *  - Enables serializable-check middleware in development to catch
 *    accidental non-serializable values (e.g. Date objects, class instances)
 *    being stored in state.
 *
 * RootState and AppDispatch are exported so TypeScript-aware hooks
 * (useAppSelector, useAppDispatch) can be typed once here and reused
 * everywhere instead of repeating the types in every component.
 */

import { configureStore } from '@reduxjs/toolkit';
import authReducer from './authSlice';

export const store = configureStore({
  reducer: {
    // The 'auth' key is what selectors reference via state.auth.*
    auth: authReducer,
  },
});

// ---------------------------------------------------------------------------
// Typed helper types
// ---------------------------------------------------------------------------

/** The full shape of the Redux state tree. Used by useAppSelector. */
export type RootState = ReturnType<typeof store.getState>;

/** The store's dispatch type, aware of thunk actions. */
export type AppDispatch = typeof store.dispatch;
