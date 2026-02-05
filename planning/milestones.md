
# Milestones


## Main Idea

The "Fadable Calendar" wants to trigger a paradigm shift in the way we think about electronical calendars. It wants to break up the blocky and rigid way conventional apps are built and instead create a more fluid and dynamic experience. The core concept is to treat time as a fading continuum, where events can fade in and out, both with time and with relevance. It wants to bridge the gap between things like notes, vague ideas and keeping-in-the-back-of-your-mind stuff and actual events that take up space and presence in the calendar.

Here are some core features, that make the "Fadable Calendar" different from other calendar apps:

+ Horizontal timelines: Instead of the traditional vertical layout, the app will use horizontal timelines to represent time. This makes users see the flow of the day rather than only its state. Also, this allows the user to scroll through days, weeks or months horizontally, which again is a fast and intuitive way to navigate.

+ Fading events: Events will be able to have warmup and cooldown times, which means they can fade in and out and do not force a hard start or ending. In the other direction, starts and ends can be marked as hard boundaries (e.g. because they were determined by someone else). This allows users to better represent the nature of their events and tasks.

+ Prioritized events: Users can mark events as more or less important, which will be reflected in the way they are displayed. More important events show more details. Less important events might step back almost entirely, just visible enough to not trigger FOMO. Users can choose the balance between information and clarity using a slider. On hover on a strip, that balance is shifted towards more information.

+ Event creation without filling out forms: Creating events will be as simple as to start typing. On hitting enter, an event is created that then can be dragged into the desired time slot. Further details can be added using inviting icons and shortcuts.

+ Iconization and preset selection based on initial title: When creating an event, the app will try to guess what kind of event it is based on the title and suggest fitting icons and presets (e.g. for duration, warmup/cooldown times, priority, etc.). This speeds up event creation and makes it more fun.

+ Widgets: Users can add widgets to their calendar, that summarize certain aspects of their schedule. There is a good selection of widgets available and every user can also create their own widgets using a simple widget builder UI.


## Planned Features

Here is a list of features and milestones that are considered for the "Fadable Calendar". They can be planned for a certain release by prefixing them with the version number. For details on the versioning scheme, see [below](#versioning-scheme).

+ Implement backend for syncing basic event changes
+ Design UI/UX to manipulate events
+ Implement backend for fadable-exclusive features
+ Implement month and year views
+ `0.x` Implement bookmarking and annotation features. Today can just be a special bookmark.
+ `0.5` Give users the possibility to vote for features and improvements to be implemented next (+ add their own).


## Roadmap

This section tries to give meaning to the version numbers and what state they are desired to represent. It is not a strict plan, but rather a guideline to help prioritize features and improvements.

### Core guideline

During development, the focus will switch constantly between the core functionality and new takes on calendar features.

### `0.1` - The Basics

The app can perform all basic functions around creating, changing and deleting events. Also, users can switch between different views (day, week, month) and navigate through the calendar. The UI/UX is raw, but already conveys the feeling of a new, never thought of take on a calendar app.

### `0.2` - Going Meta

The use of metadata to implement warmup/cooldown of events, as well as priotization, blockage types, transit times, checkpoints and so on is implemented. Users can now use these features to better organize their time.

### `0.3` - Leaving Ground

The app now feels like a better alternative to other calendar apps, due to quick navigation, pretty and informative views and assisting features. The concept of time as a fading continuum is now present in many parts of the app.

### `0.4` - Quality of Life

Users can now customize the app to their liking. They can choose from different themes, create their own custom widgets


### `0.5` - Compatibility

Various compatibility improvements are made. Users can now decide which information to paste in which fields (description, title, etc.), to make them visible in other calendar apps. In the same way, they can decide how to treat warmup and cooldown times (included in event duration or not). Also, various calendar services are supported for syncing (Google Calendar, Apple Calendar, etc.).

### `0.6` - Community Friendliness

Plugins are now a thing, and users can create and share their own plugins to add new features or change the look and feel of the app. The app also has a built-in feature voting system, where users can suggest and vote for new features and improvements.

### `1.0` - Hostablity

The app now has the technical capabilities to be hosted on a server publicly and has an onboarding process and tutorial to get new users up to speed.


## Versioning Scheme

Version numbers follow [Semantic Versioning](https://semver.org/):
- `MAJOR` version when you make incompatible API changes (`0` meaning initial development, anything may change at any time)
- `MINOR` version when you add functionality in a backwards compatible manner
- `PATCH` version when you make backwards compatible bug fixes
