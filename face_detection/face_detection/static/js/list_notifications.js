var app = new Vue({
    delimiters: ['[[', ']]'],
    el: "#app",
    data: {
        notification: [],
        empty_detalle: true,
        image_capture: '',
        show_all_list: true,
        show_white_list: false,
        show_black_list: false,
    },
    created: function(){
    },
    methods: {
        getNotification: function(pk){
            vue = this;
            var getNotificationUrl = 'get/notification/'+pk+'/';
            axios.get(getNotificationUrl)
            .then(function (response) {
                vue.notification = response.data;
                vue.empty_detalle = false;
                vue.setImageCapture(response.data.image)
            })
        },
        urlPage: function(pk){
        	return '/notification/'+pk;
        },
        setImageCapture: function(image){
            this.image_capture = 'https://via.placeholder.com/500'
            if (image != ''){ this.image_capture = image }
        },
        clearShowList: function(){
            this.show_all_list = false;
            this.show_black_list = false;
            this.show_white_list = false;
        },
        listNotifications: function(select){
            this.clearShowList();
            if (select == 1){ this.show_all_list = true }
            if (select == 2){ this.show_white_list = true }
            if (select == 3){ this.show_black_list = true }
        },
    },
});