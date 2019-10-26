var app = new Vue({
    delimiters: ['[[', ']]'],
    el: "#app",
    data: {
        grid_1: false,
        grid_2: false,
        grid_3: true,
        notifications: [],
        not_read: 0,
    },
    created: function(){
        vue = this;
        this.getNotifications();
        setInterval(function () {
          vue.getNotifications();
        }, 5000); 
    },
    methods: {
        clearGrid: function(){
            this.grid_1 = false;
            this.grid_2 = false;
            this.grid_3 = false;
        },
        changeGrid: function(value){
            this.clearGrid();
            if (value == "1" ) { this.grid_1 = true; }
            if (value == "2" ) { this.grid_2 = true; }
            if (value == "3" ) { this.grid_3 = true; }
        },
        getNotifications: function(){
            vue = this;
            var getNotificationsUrl = 'get/list/notifications';
            axios.get(getNotificationsUrl)
            .then(function (response) {
                vue.notifications = response.data.notifications;
                vue.not_read = response.data.not_read_not;
            })
        },
        getCountNotifications: function(){
            return this.notifications.length;
        },
    },
    computed: {
        emptyNotifications: function(){
            if (this.notifications.length == 0){ return true } else { return false }
        }
    },
});