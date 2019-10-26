var app = new Vue({
    delimiters: ['[[', ']]'],
    el: "#app",
    data: {
        notification: [],
        empty_detalle: true,
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
            })
        },
        urlPage: function(pk){
        	return '/notification/'+pk;
        }
    },
});