/**
 * hooks.ts — Pre-typed Redux hooks.
 *
 * Why bother?
 *  useSelector and useDispatch from react-redux are untyped by default.
 *  Wrapping them here once means every component can import useAppSelector
 *  and useAppDispatch without casting types manually.
 *
 * Usage:
 *   const isAuthenticated = useAppSelector(selectIsAuthenticated);
 *   const dispatch = useAppDispatch();
 */

import { TypedUseSelectorHook, useDispatch, useSelector } from 'react-redux';
import type { AppDispatch, RootState } from './store';

/** Dispatch hook typed to the store's AppDispatch (includes thunk support). */
export const useAppDispatch: () => AppDispatch = useDispatch;

/** Selector hook typed to the full RootState. */
export const useAppSelector: TypedUseSelectorHook<RootState> = useSelector;
