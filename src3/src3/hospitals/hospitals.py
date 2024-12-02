import random
import os
from PIL import Image, ImageDraw, ImageFont


class Space:
    def __init__(self, height, width, num_hospitals):
        """Create a new state space with given dimensions."""
        self.height = height
        self.width = width
        self.num_hospitals = num_hospitals
        self.houses = set()
        self.hospitals = set()

    def add_house(self, row, col):
        """Add a house at a particular location in the state space."""
        self.houses.add((row, col))

    def available_spaces(self):
        """Returns all cells not currently used by a house or hospital."""
        candidates = set(
            (row, col)
            for row in range(self.height)
            for col in range(self.width)
        )
        candidates -= self.houses
        candidates -= self.hospitals
        return candidates

    def hill_climb(self, maximum=None, image_prefix=None, log=False):
        """Performs hill-climbing to find a solution."""
        count = 0
        # self.hospitals = set(random.sample(self.available_spaces(), self.num_hospitals))
        self.hospitals = set(random.sample(list(self.available_spaces()), self.num_hospitals))
        if log:
            print("Initial state: cost", self.get_cost(self.hospitals))
        if image_prefix:
            self.output_image(f"{image_prefix}{str(count).zfill(3)}.png")

        while maximum is None or count < maximum:
            count += 1
            best_neighbors = []
            best_neighbor_cost = None

            for hospital in self.hospitals:
                for replacement in self.get_neighbors(*hospital):
                    neighbor = self.hospitals.copy()
                    neighbor.remove(hospital)
                    neighbor.add(replacement)
                    cost = self.get_cost(neighbor)

                    if best_neighbor_cost is None or cost < best_neighbor_cost:
                        best_neighbor_cost = cost
                        best_neighbors = [neighbor]
                    elif cost == best_neighbor_cost:
                        best_neighbors.append(neighbor)

            if best_neighbor_cost >= self.get_cost(self.hospitals):
                return self.hospitals

            self.hospitals = random.choice(best_neighbors)
            if log:
                print(f"Found better neighbor: cost {best_neighbor_cost}")

            if image_prefix:
                self.output_image(f"{image_prefix}{str(count).zfill(3)}.png")

    def random_restart(self, maximum, image_prefix=None, log=False):
        """Repeats hill-climbing multiple times."""
        best_hospitals = None
        best_cost = None

        for i in range(maximum):
            hospitals = self.hill_climb()
            cost = self.get_cost(hospitals)
            if best_cost is None or cost < best_cost:
                best_cost = cost
                best_hospitals = hospitals
                if log:
                    print(f"{i}: Found new best state: cost {cost}")
            else:
                if log:
                    print(f"{i}: Found state: cost {cost}")

            if image_prefix:
                self.output_image(f"{image_prefix}{str(i).zfill(3)}.png")

        return best_hospitals

    def get_cost(self, hospitals):
        """Calculates sum of distances from houses to the nearest hospital."""
        return sum(
            min(abs(h[0] - hospital[0]) + abs(h[1] - hospital[1]) for hospital in hospitals)
            for h in self.houses
        )

    def get_neighbors(self, row, col):
        """Returns valid neighbors for a given cell."""
        candidates = [
            (row - 1, col), (row + 1, col), (row, col - 1), (row, col + 1)
        ]
        return [
            (r, c) for r, c in candidates
            if 0 <= r < self.height and 0 <= c < self.width
            and (r, c) not in self.houses and (r, c) not in self.hospitals
        ]

    def output_image(self, filename):
        """Generates an image with all houses and hospitals."""
        cell_size = 100
        cell_border = 2
        cost_size = 40
        padding = 10
        script_dir = os.path.dirname(os.path.abspath(__file__))

        house_image_path = os.path.join(script_dir, "assets", "images", "House.png")
        hospital_image_path = os.path.join(script_dir, "assets", "images", "Hospital.png")
        font_path = os.path.join(script_dir, "assets", "fonts", "OpenSans-Regular.ttf")

        # Ensure assets exist
        if not all(map(os.path.exists, [house_image_path, hospital_image_path, font_path])):
            raise FileNotFoundError("One or more required assets are missing.")

        house = Image.open(house_image_path).resize((cell_size, cell_size))
        hospital = Image.open(hospital_image_path).resize((cell_size, cell_size))
        font = ImageFont.truetype(font_path, 30)

        img = Image.new(
            "RGBA",
            (self.width * cell_size, self.height * cell_size + cost_size + padding * 2),
            "white"
        )
        draw = ImageDraw.Draw(img)

        for i in range(self.height):
            for j in range(self.width):
                rect = [
                    (j * cell_size + cell_border, i * cell_size + cell_border),
                    ((j + 1) * cell_size - cell_border, (i + 1) * cell_size - cell_border)
                ]
                draw.rectangle(rect, fill="black")

                if (i, j) in self.houses:
                    img.paste(house, rect[0], house)
                if (i, j) in self.hospitals:
                    img.paste(hospital, rect[0], hospital)

        draw.rectangle(
            (0, self.height * cell_size, self.width * cell_size, self.height * cell_size + cost_size + padding * 2),
            "black"
        )
        draw.text(
            (padding, self.height * cell_size + padding),
            f"Cost: {self.get_cost(self.hospitals)}",
            fill="white",
            font=font
        )

        img.save(filename)


# Create a new space and add houses randomly
s = Space(height=10, width=20, num_hospitals=3)
for i in range(15):
    s.add_house(random.randrange(s.height), random.randrange(s.width))

# Use local search to determine hospital placement
hospitals = s.hill_climb(image_prefix="hospitals", log=True)
