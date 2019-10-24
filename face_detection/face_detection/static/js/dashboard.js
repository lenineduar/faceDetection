var app = new Vue({
    delimiters: ['[[', ']]'],
    el: "#app",
    data: {
        grid_1: false,
        grid_2: false,
        grid_3: true,
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
    }
});