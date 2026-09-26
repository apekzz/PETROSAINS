(function () {
    var chatForm = document.getElementById("chatForm");
    var chatInput = document.getElementById("chatInput");
    var chatLog = document.getElementById("chatLog");
    var status = document.getElementById("consultStatus");
    var out = document.getElementById("consultOut");
    var chat = { text: "", notes: [], count: null, audience: "", age: null, step: "event" };

    function threadMessages() {
        return Array.prototype.map.call(chatLog.querySelectorAll(".chat-row:not(.is-thinking)"), function (row) {
            return {
                role: row.classList.contains("user") ? "user" : "assistant",
                content: row.querySelector(".chat-bubble").textContent
            };
        });
    }

    function showThinking() {
        stopThinking();
        var row = document.createElement("div");
        row.className = "chat-row bot is-thinking";
        row.setAttribute("role", "status");
        row.setAttribute("aria-label", "Thinking");
        var bubble = document.createElement("p");
        bubble.className = "chat-bubble chat-thinking";
        for (var i = 0; i < 3; i += 1) {
            bubble.appendChild(document.createElement("span")).className = "think-dot";
        }
        row.appendChild(bubble);
        chatLog.appendChild(row);
        chatLog.scrollTop = chatLog.scrollHeight;
        chatInput.disabled = true;
    }

    function stopThinking() {
        var row = chatLog.querySelector(".is-thinking");
        if (row) row.remove();
        chatInput.disabled = false;
    }

    function say(role, text) {
        stopThinking();
        var row = document.createElement("div");
        row.className = "chat-row " + (role === "user" ? "user" : "bot");
        var bubble = document.createElement("p");
        bubble.className = "chat-bubble";
        bubble.textContent = text;
        row.appendChild(bubble);
        chatLog.appendChild(row);
        chatLog.scrollTop = chatLog.scrollHeight;
    }

    function paintRequest() {
        document.getElementById("sumEvent").textContent = chat.text || "—";
        document.getElementById("sumCount").textContent = chat.count == null ? "—" : String(chat.count);
        document.getElementById("sumGroup").textContent = chat.audience || "—";
    }

    function resetChat() {
        chat = { text: "", notes: [], count: null, audience: "", age: null, step: "event" };
        chatLog.replaceChildren();
        paintRequest();
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

    var lastFacts = null;

    function wantsElse(line) {
        return /\b(another|something else|different|don'?t want|do not want|not those|not this|instead|other thing|other item|coloring|colouring)\b/i.test(line);
    }

    function boundaryText() {
        var titles = [];
        ((lastFacts && lastFacts.recommendations) || []).forEach(function (row) {
            if (row.title && titles.indexOf(row.title) < 0) titles.push(row.title);
        });
        var listed = titles.length ? titles.join(", ") : "the options in the programme brief";
        return "I understand, and that is okay. We can only suggest these: " + listed + ". If you really want something else, please contact the person in charge.";
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

    function foldFacts(line) {
        var counted = takeCount(line);
        var bare = line.match(/^\s*(\d{1,4})\s*$/);
        if (counted) chat.count = counted;
        else if (bare) chat.count = Number(bare[1]);
        if (hasAudience(line)) chat.audience = line;
        var age = ageFrom(line);
        if (age) chat.age = age;
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
            var age = ageFrom(line);
            if (age) chat.age = age;
        } else if (chat.step === "done" && wantsElse(line)) {
            paintRequest();
            decline();
            return;
        } else if (chat.step === "done") {
            var priorCount = chat.count;
            var priorAudience = chat.audience;
            var priorAge = chat.age;
            foldFacts(line);
            if (/\bevent\b/i.test(line)) chat.text = line;
            paintRequest();
            var changed = chat.count !== priorCount || chat.audience !== priorAudience || chat.age !== priorAge || /\bevent\b/i.test(line);
            if (changed) advise();
            else followUp();
            return;
        } else {
            chat.text = line;
            foldFacts(line);
        }
        paintRequest();
        askNext();
    }

    function payload() {
        return {
            text: chat.text,
            audience: chat.audience,
            age: chat.age,
            count: chat.count,
            duration: null,
            venue: "unknown",
            electricity: "unknown",
            internet: "unknown",
            water: "unknown",
            budget: "unknown",
            accessibility: ""
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

    function showPicks(data) {
        var picks = document.createElement("div");
        picks.className = "brief-picks";
        var title = document.createElement("p");
        title.className = "brief-title";
        title.textContent = data.programme_title || "Suggested programme";
        picks.appendChild(title);
        (data.recommendations || []).forEach(function (row) {
            var card = document.createElement("article");
            card.className = "brief-pick";
            var heading = document.createElement("h3");
            heading.textContent = row.title || row.offering_id;
            card.appendChild(heading);
            if (row.reason) {
                var why = document.createElement("p");
                why.textContent = row.reason;
                card.appendChild(why);
            }
            var who = (data.in_charge || []).filter(function (person) {
                return person.offering_id === row.offering_id;
            })[0];
            if (who) {
                var charge = document.createElement("p");
                charge.className = "brief-who";
                charge.textContent = who.facilitators + " facilitators";
                card.appendChild(charge);
            }
            var lines = (data.items || []).filter(function (item) {
                return item.offering_id === row.offering_id;
            }).slice(0, 3);
            if (lines.length) {
                var list = document.createElement("ul");
                lines.forEach(function (item) {
                    var entry = document.createElement("li");
                    entry.textContent = itemQty(item);
                    list.appendChild(entry);
                });
                card.appendChild(list);
            }
            picks.appendChild(card);
        });
        if (data.alternative) {
            var booked = document.createElement("p");
            booked.className = "brief-booked";
            booked.textContent = data.alternative.title + " is already booked. " + (data.alternative.tradeoff || "");
            picks.appendChild(booked);
        }
        return picks;
    }

    function render(data) {
        out.replaceChildren();
        out.appendChild(showPicks(data));
        var more = document.createElement("details");
        more.className = "brief-more";
        var summary = document.createElement("summary");
        summary.textContent = "Full brief";
        more.appendChild(summary);
        var items = (data.items || []).map(function (row) {
            return row.offering_id + " " + row.title + ". " + itemQty(row);
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
            more.appendChild(block(pair[0], pair[1]));
        });
        out.appendChild(more);
    }

    function itemQty(item) {
        var qty = item.packs == null ? "" : " × " + item.packs;
        var store = " · not in store";
        if (item.store_available != null) {
            store = " · " + item.store_available + " available of " + item.store_total;
        }
        return (item.name || "") + qty + store;
    }

    function packFacts(data) {
        lastFacts = {
            intent: "",
            items: data.items || [],
            in_charge: data.in_charge || [],
            constraints: data.constraints_safety || [],
            warehouse: data.warehouse || { items: [], staff: [], checked_out: [] },
            recommendations: (data.recommendations || []).map(function (row) {
                return { offering_id: row.offering_id, title: row.title, reason: row.reason };
            })
        };
        return lastFacts;
    }

    function talk(facts) {
        return fetch("/api/consultant/talk", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ messages: threadMessages(), facts: facts })
        }).then(function (response) {
            return response.json();
        });
    }

    function decline() {
        var facts = Object.assign({}, lastFacts || { recommendations: [] }, { intent: "decline" });
        status.textContent = "";
        showThinking();
        talk(facts).then(function (result) {
            var reply = (result && result.reply) || "";
            say("bot", reply.toLowerCase().indexOf("person in charge") >= 0 ? reply : boundaryText());
            status.textContent = (result && result.model) || "";
        }).catch(function () {
            say("bot", boundaryText());
        });
    }

    function followUp() {
        status.textContent = "";
        showThinking();
        talk(lastFacts || {}).then(function (result) {
            say("bot", (result && result.reply) || "See the programme brief.");
            status.textContent = (result && result.model) || "";
        }).catch(function () {
            say("bot", "See the programme brief.");
        });
    }

    function advise() {
        if (!chat.text || chat.count == null || !chat.audience) {
            status.textContent = "Finish the chat: event, headcount, target group.";
            return;
        }
        status.textContent = "";
        showThinking();
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
            return talk(packFacts(data)).then(function (result) {
                say("bot", (result && result.reply) || "Catalogue scored. See the programme brief.");
                status.textContent = (result && result.model) || "";
            });
        }).catch(function (error) {
            stopThinking();
            status.textContent = error.message || "Advise failed";
        });
    }

    resetChat();

    chatForm.addEventListener("submit", function (event) {
        event.preventDefault();
        ingest(chatInput.value);
        chatInput.value = "";
        chatInput.focus();
    });

    chatInput.addEventListener("keydown", function (event) {
        if (event.key === "Enter" && !event.shiftKey) {
            event.preventDefault();
            chatForm.requestSubmit();
        }
    });

    function pingClientHello() {
        fetch("/api/client/hello", { method: "POST", cache: "no-store", keepalive: true }).catch(function () {});
    }

    pingClientHello();
    setInterval(pingClientHello, 2000);
    window.addEventListener("pagehide", function (event) {
        if (event.persisted) return;
        navigator.sendBeacon("/api/client/leave");
    });
})();
