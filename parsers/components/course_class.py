class Course:
    def __init__(self):
        self.Title = None
        self.Link = ""
        self.Author = ""
        self.Description = ""
        self.Tags = []
        self.ImageLink = ""
        self.Duration = ""
        self.Rate = 0
        self.RateCount = 0
        self.Students = 0
        self.Document = ""
        self.Language = ""
        self.Price = ""
        self.Difficulty = ""
        self.Platform = ""

    def __eq__(self, other):
        if type(other) != Course:
            return False
        try:
            self.Tags.extend(other.Tags)
            self.Tags = set(self.Tags)
        finally:
            return self.Link == other.Link

    def __hash__(self):
        return hash(self.Link)
    
    def printSelf(self):
        print("Platform:", self.Platform)
        print("Title:", self.Title)
        print("Link:", self.Link)
        print("Author:", self.Author)
        #print("Desc:", len(self.Description), "symbols")
        print("Desc:", self.Description)
        print("Tags:", self.Tags)
        print("ImageLink:", self.ImageLink)
        print("Duration:", self.Duration)
        print("Rate:", self.Rate)
        print("Rates:", self.RateCount)
        print("Students:", self.Students)
        print("Document:", self.Document)
        print("Price:", self.Price)
        print("Difficulty:", self.Difficulty)


def getCourse():
    return Course()