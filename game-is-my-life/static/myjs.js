$(document).ready(function () {
    $("#file").on('change',function(){
        var fileName = $("#file").val();
        $(".upload-name").val(fileName);
    });
});

function listing(username) {
    if (username==undefined) {
        username=""
    }
    $.ajax({
        type: "GET",
        url: `/content?username_give=${username}`,
        data: {},
        success: function (response) {
            let content = response['posts'];
            for (let i = 0; i<content.length; i++) {
                let post = content[i]
                let class_heart = ""
                if (post["heart_by_me"]) {
                    class_heart = "fa-heart"
                } else {
                    class_heart = "fa-heart-o"
                }
                let count_heart = post['count_heart']
                if (content[i]['file'] === "none") {
                    let value = `<section class="section">
                                    <div id="post-box" class="container">
                                        <div class="box">
                                            <article class="media">
                                                <div class="media-left">
                                                    <a class="image is-64x64" href="/user/${content[i]['username']}">
                                                        <img class="is-rounded" src="{{ url_for('static', filename='profile_pics/profile_placeholder.png') }}" alt="Image">
                                                    </a>
                                                </div>
                                                <div class="media-content">
                                                    <div class="content">
                                                        <p>
                                                            <strong>${post['username']}</strong> <small>@username</small> <small>10분 전</small>
                                                            <br>
                                                            ${content[i]['content']}
                                                        </p>
                                                    </div>
                                                    <nav class="level is-mobile">
                                                        <div class="level-left" id="${post["_id"]}">
                                                            <a class="level-item is-sparta" aria-label="heart" onclick="toggle_like('${post['_id']}', 'heart')">
                                                                <span class="icon is-small"><i class="fa ${class_heart}" aria-hidden="true"></i></span>&nbsp;<span class="like-num">${num2str(count_heart)}</span>
                                                            </a>
                                                        </div>
                                                    </nav>
                                                </div>
                                            </article>
                                        </div>
                                    </div>
                                </section>`;
                    $(".has-navbar-fixed-top").append(value)
                } else {
                    let value = `<section class="section">
                                    <div id="post-box" class="container">
                                        <div class="wrap">
                                            <div class="box child1" style="margin-bottom: 0px; height: 400px; width: 346px; margin-right: 10px; text-align: center;">
                                                <img src="../static/img/${content[i]['file']}" style="max-height: 360px; max-width: 310px; ">
                                            </div>
                                            <div class="box child2" style="height: 400px; width: 346px;">
                                                <div class="media">
                                                    <div class="media-left">
                                                        <a class="image is-64x64" href="/user/${content[i]['username']}">
                                                        <img class="is-rounded" src="{{ url_for('static', filename='profile_pics/profile_placeholder.png')}}" alt="Image">
                                                        </a>
                                                    </div>
                                                    <div class="media-content">
                                                        <div class="content">
                                                            <p>
                                                                <strong>${post['username']}</strong> <small>@username</small> <small>10분 전</small>
                                                            </p>
                                                        </div>
                                                        <nav class="level is-mobile">
                                                            <div class="level-left" id="${post["_id"]}">
                                                                <a class="level-item is-sparta" aria-label="heart" onclick="toggle_like('${post['_id']}', 'heart')">
                                                                    <span class="icon is-small"><i class="fa ${class_heart}" aria-hidden="true"></i></span>&nbsp;<span class="like-num">${num2str(count_heart)}</span>
                                                                </a>
                                                            </div>
                                                        </nav>
                                                    </div>
                                                </div>
                                                <div>
                                                    <p>${content[i]['content']}</p>
                                                </div>
                                            </div>
                                        </div>
                                    </div>
                                </section>`;
                        $(".has-navbar-fixed-top").append(value)
                }
            }
        }
    })
}

function post() {
    let content = $("#textarea-post").val()
    let file = $('#file')[0].files[0];
    let form_data = new FormData();

    if (file === "undefined") {
        form_data.append("content_give", content);
    } else {
        form_data.append("content_give", content);
        form_data.append("file_give", file);
    }

    $.ajax({
        type: "POST",
        url: "/content",
        data: form_data,
        cache: false,
        contentType: false,
        processData: false,
        success: function (response) {
            alert(response["msg"])
            window.location.reload()
        }
    });
}

 function sign_out() {
                $.removeCookie('mytoken', {path: '/'});
                alert('로그아웃!')
                window.location.href = "/login"
            }


function toggle_like(post_id, type) {
    console.log(post_id, type)
    let $a_like = $(`#${post_id} a[aria-label='heart']`)
    let $i_like = $a_like.find("i")
    if ($i_like.hasClass("fa-heart")) {
        $.ajax({
            type: "POST",
            url: "/update_like",
            data: {
                post_id_give: post_id,
                type_give: type,
                action_give: "unlike"
            },
            success: function (response) {
                console.log("unlike")
                $i_like.addClass("fa-heart-o").removeClass("fa-heart")
                $a_like.find("span.like-num").text(num2str(response["count"]))
            }
        })
    } else {
        $.ajax({
            type: "POST",
            url: "/update_like",
            data: {
                post_id_give: post_id,
                type_give: type,
                action_give: "like"
            },
            success: function (response) {
                console.log("like")
                $i_like.addClass("fa-heart").removeClass("fa-heart-o")
                $a_like.find("span.like-num").text(num2str(response["count"]))
            }
        })

    }
}

function num2str(count) {
    if (count > 10000) {
        return parseInt(count / 1000) + "k"
    }
    if (count > 500) {
        return parseInt(count / 100) / 10 + "k"
    }
    if (count == 0) {
        return ""
    }
    return count
}

