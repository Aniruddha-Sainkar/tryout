/* TEST CONFIG (example: a small timesheet app)
   The only file that changes the words of a test. The layout, colours, intro, timer, hints, ratings,
   badges, recording, results file and email are the Tryout standard and live in the shell. */
window.UT_CONFIG = {
  project: "Timesheet",                       // product name, shown on the intro and in the results
  version: "Example prototype v1",            // which build was tested; printed in the results header
  minutes: 5,                                 // honest estimate for the whole session
  pitch: "Timesheet is where consultants log their hours and send them for approval.",
  persona: "You're a consultant wrapping up your week on a Friday afternoon. Each moment has one task.",
  disclaimer: "People and data are made up. Nothing is sent anywhere.",
  finale: { kicker: "17:30 · Week wrapped", title: "Your week,", accent: "submitted.",
            tally: { signal: "entry-added", label: "entries logged" } },   // tally is optional
  resultsEmail: "research@example.com",      // where participants send their results file. Required
  uploadUrl: "",                              // optional shared folder link ("Can edit" for the organisation)

  tasks: [
    { id: "log", time: "16:40", title: "Catch up on yesterday",
      // The story sets the scene and ends with the ask in bold. It never names a button or a tab.
      story: "It's Friday. Yesterday you spent 6 hours on the Northwind portal redesign and never logged it. <b>Log yesterday's hours.</b>",
      // Sub-steps stay hidden until achieved, so they confirm progress without giving the route away.
      subs: [["open", "Started a new entry"], ["save", "Saved the hours"]],
      // Shown only if the participant asks, and only offered after 45 seconds.
      hint: "Look under the list of days on This week.",
      target: 90,                             // seconds before the timer says "No rush". Be generous
      badge: { name: "Caught up", icon: "clock" },
      win: "Thursday now shows 6 hours on Northwind.",
      setup: { screen: "week" },              // passed to the prototype before the task starts
      check(s, t) {
        if (s.type === "add-started") t.tick("open");
        if (s.type === "entry-added") {
          t.tick("open"); t.tick("save");
          if (s.day === "Thu" && /northwind/i.test(s.project)) t.win();
          // A near miss gets a neutral tip. The participant can still press "I'm done".
          else t.tip("Saved. The task was about Thursday on the Northwind project.");
        }
      } },

    { id: "past", time: "16:50", title: "Answer a quick question",
      story: "Your manager messages you: how many hours did you log last week? <b>Find last week's total.</b>",
      subs: [["find", "Found where past weeks live"]],
      hint: "Past weeks are not on the This week screen.",
      target: 60,
      badge: { name: "Good memory", icon: "search" },
      win: "Last week was 38.5 hours, approved.",
      // No setup: the prototype stays where the last task left it, like real life.
      check(s, t) {
        if (s.type === "tab-opened" && s.tab === "history") { t.tick("find"); t.win(); }
      } },

    { id: "submit", time: "17:20", title: "Hand it in",
      story: "Everything for this week is in. <b>Send this week's timesheet for approval.</b>",
      subs: [["start", "Started to submit"], ["sent", "Confirmed and sent"]],
      hint: "There is a Submit option on This week and another in History.",
      target: 90,
      badge: { name: "Week submitted", icon: "send" },
      win: "Priya Nair has your timesheet to approve.",
      // This task guarantees its own starting point: Thursday is filled even if task 1 was skipped.
      setup: { screen: "week", ensureThursday: true },
      // Every valid route counts. Here the week can be submitted from two places.
      check(s, t) {
        if (s.type === "submit-started") t.tick("start");
        if (s.type === "submitted") { t.tick("start"); t.tick("sent"); t.win(); }
      } }
  ]
};
