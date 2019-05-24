$(document).ready(function() {
    console.log('Document Ready!')
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

    let json_party_member = {
        'oldname': oldName,
        'name': charName,
        'tactician': parseInt(tactLv),
        'level_headed': parseInt(lvlHead),
        'quick': parseInt(quick),
        'hesitant': parseInt(hesitant),
        'type': type
    };
    console.log(json_party_member);

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

$("#home-navbutton").on("click", function() {
    $.ajax({
        url: '/home',
        method: 'GET',
        success: function(response){
            $("#page-content").html(response);
        },
        error: function(error){
            alert("failed to load home page");
        }
    });
});

$("#new-character-navbutton").on("click", function() {
    console.log("navigating to character creation");
});

$(".join-table").on('click', function(){
    // alert("join table button pushed");
    $.ajax({
        url: '/tables',
        type: 'GET',
        dataType: 'html',
        success: function(response) {
            $("#page-content").html(response);
        },
        error: function() {
            alert('Join Table GET failed');
        }
    });
});

$(".create-table").on('click', function() {
    // alert("create table button pushed");
    $.ajax({
        url: '/tables',
        type: 'GET',
        dataType: 'html',
        success: function(response) {
            $("#page-content").html(response);
        },
        error: function() {
            alert('Join Table GET failed');
        }
    });
});