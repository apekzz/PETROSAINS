(function () {
    var form = document.getElementById("consultForm");
    var chatForm = document.getElementById("chatForm");
    var chatInput = document.getElementById("chatInput");
    var chatLog = document.getElementById("chatLog");
    var status = document.getElementById("consultStatus");
    var out = document.getElementById("consultOut");
    var timePanel = document.getElementById("timePanel");
    var timeToggle = document.getElementById("timeToggle");
    var savedDuration = null;
    var chat = { text: "", count: null, audience: "", age: null, step: "event" };

    function minutesBetween(start, end) {
        var from = start.split(":").map(Number);
        var to = end.split(":").map(Number);
        return (to[0] * 60 + to[1]) - (from[0] * 60 + from[1]);
    }

    function setTimeOpen(open) {
        timePanel.classList.toggle("is-hidden", !open);
        timeToggle.setAttribute("aria-expanded", open ? "true" : "false");
    }

    function clearTime() {
        savedDuration = null;
        document.getElementById("timeToggleText").textContent = "Choose time";
        document.getElementById("startTime").value = "09:00";
        document.getElementById("endTime").value = "11:00";
        document.getElementById("timeError").textContent = "";
        setTimeOpen(false);
    }

    function threadMessages() {
        return Array.prototype.map.call(chatLog.querySelectorAll(".chat-row"), function (row) {
            return {
                role: row.classList.contains("user") ? "user" : "assistant",
                content: row.querySelector(".chat-bubble").textContent
            };
        });
    }

    function say(role, text) {
        var row = document.createElement("div");
        row.className = "chat-row " + (role === "user" ? "user" : "bot");
        var bubble = document.createElement("p");
        bubble.className = "chat-bubble";
        bubble.textContent = text;
        row.appendChild(bubble);
        chatLog.appendChild(row);
        chatLog.scrollTop = chatLog.scrollHeight;
    }

    function resetChat() {
        chat = { text: "", count: null, audience: "", age: null, step: "event" };
        chatLog.replaceChildren();
        say("bot", "What event is this?");
    }

    function ageFrom(text) {
        var aged = text.match(/\b(?:age|aged)\s*(\d{1,2})\b/i);
        if (aged) return Number(aged[1]);
        var years = text.match(/\b(\d{1,2})\s*(?:\+|years?|yo)\b/i);
        return years ? Number(years[1]) : null;
    }

    function hasAudience(text) {
        return /\b(primary|secondary|tertiary|teacher|teachers|public|kindergarten)\b/i.test(text);
    }

    function takeCount(text) {
        var hit = text.match(/\b(\d{1,4})\s*(?:people|person|students?|pax|participants|kids|children)\b/i);
        return hit ? Number(hit[1]) : null;
    }

    function askNext() {
        if (chat.count == null) {
            chat.step = "count";
            say("bot", "How many people?");
            return;
        }
        if (!chat.audience) {
            chat.step = "group";
            say("bot", "Target group?");
            return;
        }
        chat.step = "done";
        advise();
    }

    function ingest(raw) {
        var line = raw.trim();
        if (!line) return;
        say("user", line);
        if (chat.step === "count") {
            var digits = line.match(/\b(\d{1,4})\b/);
            if (!digits) {
                say("bot", "How many people? Use a number.");
                return;
            }
            chat.count = Number(digits[1]);
        } else if (chat.step === "group") {
            chat.audience = line;
            chat.age = ageFrom(line);
        } else {
            chat.text = line;
            chat.count = takeCount(line);
            chat.audience = hasAudience(line) ? line : "";
            chat.age = ageFrom(line);
        }
        askNext();
    }

    function payload() {
        return {
            text: chat.text,
            audience: chat.audience,
            age: chat.age,
            count: chat.count,
            duration: savedDuration,
            venue: document.getElementById("reqVenue").value,
            electricity: document.getElementById("reqPower").value,
            internet: document.getElementById("reqNet").value,
            water: document.getElementById("reqWater").value,
            budget: document.getElementById("reqBudget").value,
            accessibility: document.getElementById("reqAccess").value.trim()
        };
    }

    function block(title, lines) {
        var section = document.createElement("section");
        section.className = "out-block";
        var heading = document.createElement("h3");
        heading.textContent = title;
        section.appendChild(heading);
        var items = (lines || []).filter(function (line) { return line; });
        if (!items.length) {
            var empty = document.createElement("p");
            empty.textContent = "None.";
            section.appendChild(empty);
            return section;
        }
        if (items.length === 1) {
            var paragraph = document.createElement("p");
            paragraph.textContent = items[0];
            section.appendChild(paragraph);
            return section;
        }
        var list = document.createElement("ul");
        items.forEach(function (line) {
            var item = document.createElement("li");
            item.textContent = line;
            list.appendChild(item);
        });
        section.appendChild(list);
        return section;
    }

    function render(data) {
        out.replaceChildren();
        var items = (data.items || []).map(function (row) {
            var qty = row.packs == null ? "qty not on sheet" : "× " + row.packs;
            return row.offering_id + " " + row.title + ". " + row.name + " " + qty;
        });
        var charge = (data.in_charge || []).map(function (row) {
            return row.title + " needs " + row.facilitators + " facilitators.";
        });
        var picks = (data.recommendations || []).map(function (row) {
            var rule = (row.rules || []).join(", ");
            return row.offering_id + " " + row.title + " (" + row.kit + "). " + (row.reason || "") + (rule ? " " + rule : "");
        });
        var journey = (data.journey || []).map(function (step) {
            return step.offering_id + " " + step.title + ". Setup " + step.setup_min + " min. Delivery " + step.duration_min + " min. " + (step.method || "");
        });
        var alt = data.alternative
            ? [data.alternative.offering_id + " " + data.alternative.title + " is booked. " + (data.alternative.tradeoff || "")]
            : [];
        [
            ["Recommended items", items],
            ["In charge", charge],
            ["Understanding", [data.understanding]],
            ["Missing questions", data.missing_questions],
            ["Assumptions", data.assumptions],
            ["Recommended offerings", picks],
            ["Programme title", [data.programme_title]],
            ["Storyline", [data.storyline]],
            ["Participant journey", journey],
            ["Proposed enhancements", data.enhancements],
            ["Constraints and safety", data.constraints_safety],
            ["Alternative", alt],
            ["Rotations", data.rotations]
        ].forEach(function (pair) {
            out.appendChild(block(pair[0], pair[1]));
        });
    }

    function advise() {
        if (!chat.text || chat.count == null || !chat.audience) {
            status.textContent = "Finish the chat: event, headcount, target group.";
            return;
        }
        status.textContent = "Scoring catalogue…";
        out.replaceChildren();
        fetch("/api/consultant/advise", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(payload())
        }).then(function (response) {
            return response.json().then(function (data) {
                if (!response.ok) throw new Error(data.detail || "Advise failed");
                return data;
            });
        }).then(function (data) {
            status.textContent = "Writing the reply…";
            render(data);
            return fetch("/api/consultant/talk", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    messages: threadMessages(),
                    facts: {
                        items: data.items || [],
                        in_charge: data.in_charge || [],
                        recommendations: (data.recommendations || []).map(function (row) {
                            return { offering_id: row.offering_id, title: row.title, reason: row.reason };
                        })
                    }
                })
            }).then(function (response) {
                return response.json();
            }).then(function (talk) {
                say("bot", (talk && talk.reply) || "Catalogue scored. See the programme brief.");
                status.textContent = (talk && talk.model) || "";
            });
        }).catch(function (error) {
            status.textContent = error.message || "Advise failed";
        });
    }

    resetChat();

    document.getElementById("btnExample").addEventListener("click", function () {
        resetChat();
        clearTime();
        document.getElementById("reqVenue").value = "unknown";
        document.getElementById("reqPower").value = "unknown";
        document.getElementById("reqNet").value = "unknown";
        document.getElementById("reqWater").value = "unknown";
        document.getElementById("reqBudget").value = "unknown";
        document.getElementById("reqAccess").value = "";
        ingest("LEGO and robot");
    });

    chatForm.addEventListener("submit", function (event) {
        event.preventDefault();
        ingest(chatInput.value);
        chatInput.value = "";
    });

    timeToggle.addEventListener("click", function () {
        setTimeOpen(timePanel.classList.contains("is-hidden"));
    });

    document.getElementById("saveTime").addEventListener("click", function () {
        var start = document.getElementById("startTime").value;
        var end = document.getElementById("endTime").value;
        var gap = minutesBetween(start, end);
        if (!start || !end || gap <= 0) {
            document.getElementById("timeError").textContent = "End time must be after start time.";
            return;
        }
        savedDuration = gap;
        document.getElementById("timeToggleText").textContent = start + "–" + end + " · " + gap + " min";
        document.getElementById("timeError").textContent = "";
        setTimeOpen(false);
    });

    document.addEventListener("click", function (event) {
        if (!event.target.closest(".time-picker")) setTimeOpen(false);
    });

    form.addEventListener("submit", function (event) {
        event.preventDefault();
        advise();
    });
})();
