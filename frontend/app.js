
// =============================== Constants ===============================
// - Input constants
const WEEKS_PER_BATCH = 4;

// - Get references to key DOM elements
const calendarScrollview = document.getElementById("calendar-scrollview");
const mainScroller = document.getElementById("main-scroller");
const bufferTop = document.getElementById("scroll-buffer-top");
const bufferBottom = document.getElementById("scroll-buffer-bottom");

// - Calculate the start of the current week (week starts on Monday)
const today = new Date();
const thisWeekStart = getWeekStart(today);
const renderedWeeks = new Set();
const weekLoadPromises = new Map();

// =============================== Variables ===============================
let earliestWeekStart = null;
let latestWeekStart = null;

// =============================== Functions ===============================

function addDays(date, days) {  // Utility function to add (or subtract) days to a date
  const d = new Date(date);
  d.setDate(d.getDate() + days);
  return d;
}

async function loadWeekContent(parentElement, aroundDate) {
  try {
    const aroundDateIso = formatDateId(aroundDate);
    const response = await fetch(`/api/get_week?around_date_str=${aroundDateIso}`);
    if (!response.ok) {
      throw new Error(`Request failed with status ${response.status}`);
    }
    const html = await response.text();
    parentElement.innerHTML = html;
  } catch (error) {
    parentElement.innerHTML = "<div class=\"week-error\">Failed to load week content</div>";
    console.error("Failed to load week content!", error);
  }
}

function getWeekStart(date) {  // Get the start date of the week containing the given date (Monday start)
  const dayOfWeek = (date.getDay() + 6) % 7; // Monday = 0
  return addDays(date, -dayOfWeek);
}

function formatDateId(date) {  // Format a date as YYYY-MM-DD for use in IDs and API calls
  const year = date.getFullYear();
  const month = String(date.getMonth() + 1).padStart(2, "0");
  const day = String(date.getDate()).padStart(2, "0");
  return `${year}-${month}-${day}`;
}

function weekKey(date) {  // Generate a unique key for a week based on its start date
  const weekStart = getWeekStart(date);
  return formatDateId(weekStart);
}

function buildWeekElement(aroundDate) {  // Create a new week element, set its ID and class, and load its content
  const key = weekKey(aroundDate);
  const weekElement = document.createElement("div");
  weekElement.id = `week-${key}`;
  weekElement.className = "week-container";
  weekElement.innerHTML = "<div class=\"week-loading\">Loading...</div>";
  const loadPromise = loadWeekContent(weekElement, aroundDate)
    .finally(() => {
      weekLoadPromises.delete(key);
    });
  weekLoadPromises.set(key, loadPromise);
  return weekElement;
}

function appendWeek(aroundDate) {  // Append a week element to the end of the weeks container if it hasn't been rendered yet
  const key = weekKey(aroundDate);
  if (renderedWeeks.has(key)) {
    return null;
  }
  renderedWeeks.add(key);
  const weekElement = buildWeekElement(aroundDate);
  mainScroller.appendChild(weekElement);
  return weekLoadPromises.get(key) || null;
}

function prependWeek(aroundDate) {  // Prepend a week element to the beginning of the weeks container if it hasn't been rendered yet
  const key = weekKey(aroundDate);
  if (renderedWeeks.has(key)) {
    return null;
  }
  renderedWeeks.add(key);
  const weekElement = buildWeekElement(aroundDate);
  mainScroller.prepend(weekElement);
  return weekLoadPromises.get(key) || null;
}

function loadInitialWeeks() {  // Load weeks around the current week
  const initialLoadPromises = [];
  earliestWeekStart = thisWeekStart;
  latestWeekStart = thisWeekStart;
  for (let i = WEEKS_PER_BATCH; i > 0; i -= 1) {
    const weekStart = addDays(thisWeekStart, -7 * i);
    earliestWeekStart = weekStart;
    const loadPromise = appendWeek(weekStart);
    if (loadPromise) {
      initialLoadPromises.push(loadPromise);
    }
  }
  const baseLoadPromise = appendWeek(thisWeekStart);
  if (baseLoadPromise) {
    initialLoadPromises.push(baseLoadPromise);
  }

  for (let i = 1; i <= WEEKS_PER_BATCH; i += 1) {
    const weekStart = addDays(thisWeekStart, 7 * i);
    latestWeekStart = weekStart;
    const loadPromise = appendWeek(weekStart);
    if (loadPromise) {
      initialLoadPromises.push(loadPromise);
    }
  }
  const settleInitialLoads = initialLoadPromises.length
    ? Promise.allSettled(initialLoadPromises)
    : Promise.resolve();

  settleInitialLoads.then(() => {
    requestAnimationFrame(() => {
      const baseKey = weekKey(thisWeekStart);
      const baseElement = document.getElementById(`week-${baseKey}`);
      if (baseElement) {
        baseElement.scrollIntoView({ block: "start" });
      }
    });
  });
}

function loadWeeksBefore() {  // Load weeks before the earliest loaded week
  if (!earliestWeekStart) {
    return;
  }

  const previousScrollHeight = calendarScrollview.scrollHeight;
  for (let i = 1; i <= WEEKS_PER_BATCH; i += 1) {
    const weekStart = addDays(earliestWeekStart, -7);
    earliestWeekStart = weekStart;
    prependWeek(weekStart);
  }
  const newScrollHeight = calendarScrollview.scrollHeight;
  calendarScrollview.scrollTop += newScrollHeight - previousScrollHeight;
}

function loadWeeksAfter() {  // Load weeks after the latest loaded week
  if (!latestWeekStart) {
    return;
  }
  for (let i = 1; i <= WEEKS_PER_BATCH; i += 1) {
    const weekStart = addDays(latestWeekStart, 7);
    latestWeekStart = weekStart;
    appendWeek(weekStart);
  }
}

function setupObservers() {  // Set up IntersectionObservers to load weeks when buffers come into view
  const observer = new IntersectionObserver(
    (entries) => {
      entries.forEach((entry) => {
        if (!entry.isIntersecting) {
          return;
        }

        if (entry.target === bufferTop) {
          loadWeeksBefore();
        }
        if (entry.target === bufferBottom) {
          loadWeeksAfter();
        }
      });
    },
    {
      root: calendarScrollview,
      rootMargin: "300px 0px",
      threshold: 0,
    }
  );

  observer.observe(bufferTop);
  observer.observe(bufferBottom);
}

loadInitialWeeks();
setupObservers();
