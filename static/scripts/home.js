$(document).ready(function() {
    console.log('page loaded')
    $.ajax({
        type: 'GET',
        url: '/party',
        dataType: "html",
        success: function(response) {
            $('#page-content').html(response);
        },
        error: function(e) {
            alert('No Party Received');
        }
    });
});

$("#startInitiative").on("click", function(){
    alert("starting initative...")
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
    
    let sessionID = $("#party").attr('data-sessionid');

    let json_party_member = {
        'name': charName,
        'tactician': parseInt(tactLv),
        'level_headed': parseInt(lvlHead),
        'quick': parseInt(quick),
        'hesitant': parseInt(hesitant)
    };
    console.log(json_party_member);

    $.ajax({
        type: 'POST',
        url: '/' + sessionID + '/party/' + oldName.replace(" ", "-").toLowerCase(),
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

$("#start-initiative-btn").on("click", function() {

});

$("#new-character-navbutton").on("click", function() {
    $("#modal-charname-input").val("");
    $("#levelHeaded0").prop('checked', true);
    $(".lvlheadlabel0").addClass("active");
    $("#levelHeaded1").prop('checked', false);
    $(".lvlheadlabel1").removeClass("active");
    $("#levelHeaded2").prop('checked', false);
    $(".lvlheadlabel2").removeClass("active");

    $("#tactician0").prop('checked', true);
    $(".tactlabel0").addClass("active");
    $("#tactician1").prop('checked', false);
    $(".tactlabel1").removeClass("active");
    $("#tactician2").prop('checked', false);
    $(".tactlabel2").removeClass("active");

    $("#noQuickHesitant").prop('checked', true);
    $(".nonelabel").addClass("active");
    $("#quickEdge").prop('checked', false);
    $(".quicklabel").removeClass("active");
    $("#hesitantHindrance").prop('checked', false);
    $(".hesitantlabel").removeClass("active");
    
    console.log($("#character-modal"));
    $("#character-modal").modal();
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