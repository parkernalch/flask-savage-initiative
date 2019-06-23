$(document).ready(function() {
    console.log("Table Loaded");
    var activeIndex = 0;
    var currentRound = 0;
    var jsonResponse = null;
    let gameid = $("#table-content").data("gameid");

    const socket = io.connect("http://" + document.domain + ":" + location.port);

    $("#navbar-brand").on('click', function(){
        console.log("socket disconnecting...");
        socket.disconnect();
    });

    socket.on("connect", function(){
        console.log("socket connecting...");
        let roomData = {
            room: gameid
        };
        socket.emit('join', roomData);
    });

    socket.on("disconnect", function(){
        console.log("socket disconnecting...");
        let roomData = {
            room: 0,
            username: 'parker'
        };
        socket.emit('leave', roomData);
    });

    socket.on("update", function(data){
        // $("#table-content").html(data['html']);
        // console.log("UPDATING VIEW");
        jdata = JSON.parse(data);
        UpdateView(jdata);
    });

    socket.on("advance", function(index){
        // console.log("ADVANCING VIEW");
        activeIndex = index;
        // console.log(activeIndex);
        AdvanceRound();
    });

    socket.on("refresh", function(){
        currentRound--;
        fetchNextRound();
    });

    console.log("GameID:" ,gameid);
    fetchNextRound();

    function fetchNextRound(){
        currentRound++;
        $.ajax({
            url: "/initiative/" + gameid + "/json/" + currentRound.toString(),
            method: 'GET',
            dataType: 'text',
            success: function(response){
                jsonResponse = JSON.parse(response);
                console.log(jsonResponse);

                socket.emit("update view", JSON.stringify(jsonResponse));
                // UpdateView(jsonResponse);
                activeIndex = 0;
            },
            error: function(xhr, err, status){
                console.log(err);
                console.log(xhr);
                console.log(status);
            }
        });
        
    }

    function fetchThisRound(){
        console.log("fetching this round");
        currentRound--;
        fetchNextRound();
    }

    function UpdateView(response){
        console.log("Updating view...");
        $("#current-round-h3").html("CURRENT ROUND: " + response.round.toString());
        currentRound = response.round;

        $("#on-deck-list").empty();
        for(var character of response.party){
            let newchar = $("<li>" + character.name + "</li>");

            if(character.name == $("#player-hand-container").data("character")){
                PopulatePlayerHand(character);
            }

            newchar.addClass("on-deck-character");
            if(character.active > 0){
                newchar.addClass("active");

                $("#current-character-header").html("ACTIVE CHARACTER: " + character.name);
                
                GetPortrait(character);

                LoadInitiativeCards(character);

                LoadTacticianCards(character);
            }
            $("#on-deck-list").append(newchar);
        }
    }

    function GetPortrait(character){
        // val = null;
        // for(let key of Object.keys(characterPortraits)){
        //     if(key == character.name.toLowerCase()){
        //         val = characterPortraits[key];
        //     }
        // }
        // // $("#character-portrait").html("<img src='" + url + "' width='100' height='100'>");
        // let color = val.split(' ')[0];
        // let icon = val.split(' ')[1];

        let color = character.color;
        let icon = character.icon;

        let portrait = $("<i/>");
        portrait.attr("class", icon + " " + color);
        $("#character-portrait").html(portrait);
    }

    function AdvanceRound(){
        // console.log("getting next round in function: ", activeIndex);

        if(activeIndex >= jsonResponse.party.length){
            fetchNextRound();
            return;
        }

        let newCharacter = jsonResponse.party[activeIndex];
        $("#current-character-header").html("ACTIVE CHARACTER: " + newCharacter.name);

        let onDeckChildren = $("#on-deck-list li");
        for(let li of onDeckChildren){
            let item = $(li);

            if(item.text() === newCharacter.name){
                item.addClass("active");
            } else {
                if(item.hasClass("active")){
                    item.removeClass("active");
                }
            }
        }

        GetPortrait(newCharacter);

        LoadInitiativeCards(newCharacter);

        LoadTacticianCards(newCharacter);
    }

    function LoadInitiativeCards(character){
        $("#active-cards-in-hand").empty();
        for(var card of character.cards.hand){
            let c = $("<button/>");
            c.addClass("initiative-card");
            c.addClass("btn btn-default initiative-card");
            c.attr("cardname", card);
            c.html("<img src='../../../static/assets/" + card +  ".png' width='64' height='96'>")
            $("#active-cards-in-hand").append(c);
        }
    }

    function LoadTacticianCards(character){
        $("#tactician-cards-in-hand").empty();
        for(var card of character.cards.tactician){
            let c = $("<button/>");
            c.addClass("initiative-card");
            c.addClass("btn btn-default tactician-card");
            c.attr("cardname", card);
            c.html("<img src='../../../static/assets/" + card +  ".png' width='64' height='96'>")
            $("#tactician-cards-in-hand").append(c);
        }
    }

    function PopulatePlayerHand(character){
        $("#player-cards-in-hand").empty();
        for(var card of character.cards.hand){
            let c = $("<button/>");
            // c.addClass("initiative-card");
            c.addClass("btn btn-default player-initiative-card");
            c.attr("cardname", card);
            c.html("<img src='../../../static/assets/" + card +  ".png' width='64' height='96'>")
            $("#player-cards-in-hand").append(c);
        }
        $("#player-tact-in-hand").empty();
        for(var card of character.cards.tactician){
            let c = $("<button/>");
            // c.addClass("initiative-card");
            c.addClass("btn btn-default player-tactician-card");
            c.attr("cardname", card);
            c.attr("charname", character.name);
            c.html("<img src='../../../static/assets/" + card +  ".png' width='64' height='96'>")
            $("#player-tact-in-hand").append(c);
        }

        $(".player-tactician-card").on('click', function(){
            let card = $(this).attr("cardname");
            $("#modal-tact-card-image").html("<img src='../../../static/assets/" + card + ".png' width='64' height='96'>");
            
            $("#modal-tactician-select").empty();
            $("#modal-tactician-select").append("<option>Choose an Ally...</option>");
            for(var character of jsonResponse.party){
                $("#modal-tactician-select").append("<option>" + character.name + "</option>");
            }
            
            $("#modal-tactician-select").attr("origin", $(this).attr("charname"));
            $("#modal-tactician-select").attr("card", card);

            $("#tactician-modal").modal();
        });
    }

    $("#tactician-submit-modal").on("click", function(){
        let originName = $("#modal-tactician-select").attr("origin");
        let destinationName = $("#modal-tactician-select").val();
        let card = $("#modal-tactician-select").attr("card");

        let origin = null;
        let destination = null;

        for(var i=0; i < jsonResponse.party.length; i++){
            if(jsonResponse.party[i].name === originName){
                origin = jsonResponse.party[i];
            } else if (jsonResponse.party[i].name === destinationName){
                destination = jsonResponse.party[i];
            }
        }

        if(!origin || !destination){
            alert("Something went wrong: " + origin + ", " + destination);
            return
        }

        GiveTacticianCard(origin, destination, card);
    });

    function GiveTacticianCard(character1, character2, card){
        let origin = character1.cards.tactician;
        let destination = character2.cards.hand;
        let tactCard = card;

        if(origin.includes(card)){
            destination.push(card);
            for(var i = 0; i < origin.length; i++){
                if(origin[i] === card){
                    origin.splice(i, 1);
                    break;
                }
            }
        }

        character1.cards.tactician = origin;
        character2.cards.hand = destination;

        for (var j = 0; j < jsonResponse.party.length; j++){
            if(jsonResponse.party[j].name == character1.name){
                jsonResponse.party[j] = character1;
            } else if (jsonResponse.party[j] == character2.name){
                jsonResponse.party[j] = character2;
            }
        }

        // UpdateView(jsonResponse);

        let data = {
            origin: character1,
            destination: character2,
            card: card,
            id: gameid
        };

        console.log(data);

        $.ajax({
            url: '/tables/givecard',
            method: 'POST',
            contentType: 'application/json',
            dataType: 'html',
            data: JSON.stringify(data),
            success: function(response){
                console.log(response);
                if(response == 'ok'){
                    // console.log("emitting update view");
                    // socket.emit("update view", JSON.stringify(jsonResponse));
                    // fetchThisRound();
                    socket.emit("refresh view");
                }
            },
            error: function(xhr, err, status) {
                console.log(err);
            }
        });
        return
    }

    $("#gm-next-round").on("click", function(){
        // console.log("getting next round: ", activeIndex);
        activeIndex++;
        $.ajax({
            url: '/redis/index/increment/' + gameid,
            method: 'GET',
            success: function(response){
                // console.log(response.index);
                // console.log(activeIndex);
            },
            error: function(xhr, err, status){
                print(err);
            }
        });
        socket.emit("advance round", activeIndex);
        // AdvanceRound();
    });

});