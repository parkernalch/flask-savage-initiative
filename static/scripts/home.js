$(document).ready(function() {
    console.log('Document Ready!');
    var party = null;

    if (localStorage.getItem("party") != null){
        party = JSON.parse(localStorage.getItem("party"));
        // console.log(party);

        if(party.length > 0){
            // console.log("Party found:", party);
            var data = {
                'party': party
            };
    
            $.ajax({
                url: '/encounter/load',
                method: 'POST',
                dataType: 'html',
                contentType: 'application/json',
                data: JSON.stringify(data),
                success: function(response){
                    $("#page-content").html(response);
                },
                error: function(xhr, status, err){
                    console.log(status);
                }
            });
        } else {
            // console.log("No party found");
            $.ajax({
                url: '/encounter',
                method: 'GET',
                dataType: 'html',
                success: function(response){
                    // alert('setting page response');
                    $("#page-content").html(response);
                },
                error: function(xhr, status, err){
                    console.log(status);
                }
            });
        }
    }else {
        // console.log("No party found");
        $.ajax({
            url: '/encounter',
            method: 'GET',
            dataType: 'html',
            success: function(response){
                // alert('setting page response');
                $("#page-content").html(response);
            },
            error: function(xhr, status, err){
                console.log(status);
            }
        });
    }
});

$("#join-table-navbutton").on('click', function(){
    console.log("opening table modal");
    $("#table-modal").modal();
});

$("#game-link-input").change(function(){
    let id = $(this).val();
    $.ajax({
        url: 'tables/check/' + id,
        method: 'GET',
        success: function(response){
            console.log(response);
            if(response.status != 'ok'){
                return
            }
            $("#game-link-input").prop("disabled", true);
            for(let character of response.party){
                console.log(character);
                // $("#modal-character-select").append(option);
                $("#modal-character-select").append("<option>" + character + "</option>");
                $("#modal-character-select").prop("disabled", false);
            }
        },
        error: function(xhr, err, status){
            console.log(err);
        }
    });
});

$("#table-submit-modal").on('click', function(){
    let id = $("#game-link-input").val();
    let charname = $("#modal-character-select").val();
    
    console.log(id, charname);

    window.location.assign('/tables/join/' + id + "/" + charname.replace(" ", "%20"));
});

$("#submit-modal").on('click', function(){
    console.log("Modal Submit called");
    let oldName = $("#character-modal").attr("data-oldname");
    if(oldName === ""){
        oldName = "new character"
    }
    let charName = $("#modal-charname-input").val();
    let tactLv = $("input[type=radio][name=tacticianOptions]:checked").val() || 0;
    let lvlHead = $("input[type=radio][name=levelHeadedOptions]:checked").val() || 0;
    let quick = $("input[type=radio][name=otherOptions][id=quickEdge]:checked").val() || 0;
    let hesitant = $("input[type=radio][name=otherOptions][id=hesitantHindrance]:checked").val() || 0;
    
    // let sessionID = $("#party").attr('data-sessionid');
    let type = 'create';
    if (oldName != "new character"){
        type = 'update';
    }

    let portrait = $("#modal-portrait-icon");
    let icon = portrait.data("icon");
    let color = portrait.data("color");
    console.log("ICON: ", icon);
    console.log("COLOR: ", color);

    let json_party_member = {
        'oldname': oldName,
        'name': charName,
        'tactician': parseInt(tactLv),
        'level_headed': parseInt(lvlHead),
        'quick': parseInt(quick),
        'hesitant': parseInt(hesitant),
        'type': type,
        'icon': icon,
        'color': color
    };
    // console.log(json_party_member);

    $.ajax({
        type: 'POST',
        url: '/encounter',
        data: JSON.stringify(json_party_member),
        dataType: 'html',
        contentType: 'application/json',
        success: function(response) {
            // console.log(response);
            $("#page-content").html(response);
            $("#character-modal").modal('toggle');
        },
        error: function(e) {
            alert('POST FAILED');
        }

    });
});

$("#delete-character-modal").on("click", function() {
    console.log('deleting character');
    let charname = $("#modal-charname-input").val();
    let data = {
        'oldname': charname,
        'type': 'delete'
    }
    $.ajax({
        url: '/encounter',
        method: 'POST',
        dataType: 'html',
        contentType: 'application/json',
        data: JSON.stringify(data),
        success: function(response){
            $("#page-content").html(response);
            $("#character-modal").modal('toggle');
        },
        error: function() {
            alert("Failed to delete character " + charname);
        }
    })
});

$(".icon-grid-item").on('click', function(event){
    console.log(event);
    let i = $(event.target);
    let icon = i.attr("class");
    let colors = ['red', 'blue', 'orange', 'green', 'violet', 'light-gray', 'dark-gray', 'black'];
    let classList = $("#modal-portrait-icon").attr("class");
    let color = 'black';
    for(let cls of classList.split(' ')){
        if(colors.includes(cls)){
            color = cls;
            break;
        }
    }
    $("#modal-portrait-icon").attr("class", "mx-auto "+ icon + " " + color);
    $("#modal-portrait-icon").data("icon", icon);
    $("#modal-portrait-icon").data("color", color);
});

$(".color-button").on('click', function(event){
    console.log(event);
    let i = $(event.target);
    let color = i.data("color");
    let colors = ['red', 'blue', 'orange', 'green', 'violet', 'light-gray', 'dark-gray', 'black'];
    for(let c of colors){
        if($("#modal-portrait-icon").hasClass(c) && c != color){
            $("#modal-portrait-icon").removeClass(c);
        } else if(!$("#modal-portrait-icon").hasClass(c) && c === color){
            $("#modal-portrait-icon").addClass(c);
            $("#modal-portrait-icon").data("color", c);
        }
        continue;
    }
    
});