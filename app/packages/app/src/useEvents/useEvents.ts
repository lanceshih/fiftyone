import type { Session } from "@fiftyone/state";
import { snakeCase } from "lodash";
import { type MutableRefObject, useCallback, useMemo } from "react";
import type { Queries } from "../makeRoutes";
import type { RoutingContext } from "../routing";
import { type AppReadyState, EVENTS } from "./registerEvent";

const HANDLERS = {};

const useEvents = (
  controller: AbortController,
  router: RoutingContext<Queries>,
  readyStateRef: MutableRefObject<AppReadyState>,
  session: MutableRefObject<Session>
) => {
  const eventNames = useMemo(() => Object.keys(EVENTS), []);
  const subscriptions = useMemo(() => eventNames.map(snakeCase), [eventNames]);

  const ctx = useMemo(
    () => ({ controller, router, readyStateRef, session }),
    [controller, router, readyStateRef, session]
  );
  for (let index = 0; index < eventNames.length; index++) {
    HANDLERS[eventNames[index]] = EVENTS[eventNames[index]](ctx);
  }

  return {
    subscriptions,
    handler: useCallback((event: string, payload: string) => {
      if (event === "ping" || event === "") {
        return;
      }

      if (!HANDLERS[event]) {
        throw new Error(`event "${event}" is not registered`);
      }
      HANDLERS[event](JSON.parse(payload));
    }, []),
  };
};

export default useEvents;
