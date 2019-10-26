var app = new Vue({
    delimiters: ['[[', ']]'],
    el: "#app",
    data: {
        notification: [],
        empty_detalle: true,
        image_capture: ''
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
    },
});