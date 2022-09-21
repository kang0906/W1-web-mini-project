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
                                                            <strong>홍길동</strong> <small>@username</small> <small>10분 전</small>
                                                            <br>
                                                            ${content[i]['content']}
                                                        </p>
                                                    </div>
                                                    <nav class="level is-mobile">
                                                        <div class="level-left">
                                                            <a class="level-item is-sparta" aria-label="heart" onclick="toggle_like('', 'heart')">
                                                                <span class="icon is-small"><i class="fa fa-heart" aria-hidden="true"></i></span>&nbsp;<span class="like-num">2.7k</span>
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
                                                                <strong>홍길동</strong> <small>@username</small> <small>10분 전</small>
                                                            </p>
                                                        </div>
                                                        <nav class="level is-mobile">
                                                            <div class="level-left">
                                                                <a class="level-item is-sparta" aria-label="heart" onclick="toggle_like('', 'heart')">
                                                                    <span class="icon is-small"><i class="fa fa-heart" aria-hidden="true"></i></span>&nbsp;<span class="like-num">2.7k</span>
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
